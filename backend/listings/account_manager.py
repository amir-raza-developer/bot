# ==========================================
# 👥 BULK ACCOUNT MANAGEMENT MODULE
# ==========================================

from django.db import models
from django.utils import timezone
import json
from datetime import datetime

# ==========================================
# FACEBOOK ACCOUNT MODEL
# ==========================================
class FacebookAccount(models.Model):

    class Meta:
        app_label = 'listings'

    ACCOUNT_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('banned', 'Banned'),
        ('restricted', 'Restricted'),
        ('suspended', 'Suspended'),
    ]
    
    ACCOUNT_AGE = [
        ('new', 'New (< 3 months)'),
        ('medium', 'Medium (3-12 months)'),
        ('old', 'Old (> 1 year)'),
    ]
    
    phone_or_email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255, null=True, blank=True)
    
    # Account info
    status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='active')
    account_age = models.CharField(max_length=20, choices=ACCOUNT_AGE, default='new')
    verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Statistics
    listings_created = models.IntegerField(default=0)
    listings_sold = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ban_count = models.IntegerField(default=0)
    warning_count = models.IntegerField(default=0)
    
    # Rate limiting
    last_action = models.DateTimeField(null=True, blank=True)
    daily_limit = models.IntegerField(default=50)
    daily_used = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account_name or self.phone_or_email} ({self.status})"
    
    def can_publish_listings(self):
        """Check if account can publish listings."""
        if self.status != 'active':
            return False
        if self.daily_used >= self.daily_limit:
            return False
        if self.ban_count > 3:
            return False
        return True

# ==========================================
# ACCOUNT POOL MANAGER
# ==========================================
class AccountPoolManager:

    class Meta:
        app_label = 'listings'

    def __init__(self):
        self.active_accounts = []
        self.account_rotation_index = 0
    
    def get_all_accounts(self):
        """Get all Facebook accounts."""
        return FacebookAccount.objects.all()
    
    def get_active_accounts(self):
        """Get only active accounts."""
        return FacebookAccount.objects.filter(status='active')
    
    def get_available_account(self):
        """Get next available account for publishing."""
        return FacebookAccount.objects.filter(
            status='active',
            daily_used__lt=models.F('daily_limit')
        ).order_by('daily_used').first()
    
    def add_account(self, phone_or_email, password, account_name=None):
        """Add new account to pool."""
        account, created = FacebookAccount.objects.get_or_create(
            phone_or_email=phone_or_email,
            defaults={'password': password, 'account_name': account_name}
        )
        return account, created
    
    def get_account_details(self, account_id):
        """Get detailed account information."""
        account = FacebookAccount.objects.get(id=account_id)
        return {
            'id': account.id,
            'email': account.phone_or_email,
            'name': account.account_name,
            'status': account.status,
            'listings_created': account.listings_created,
            'listings_sold': account.listings_sold,
            'earnings': float(account.total_earnings),
            'ban_count': account.ban_count,
            'can_publish': account.can_publish_listings(),
            'daily_used': account.daily_used,
            'daily_limit': account.daily_limit,
        }
    
    def get_pool_stats(self):
        """Get statistics about account pool."""
        accounts = self.get_all_accounts()
        return {
            'total_accounts': accounts.count(),
            'active_accounts': self.get_active_accounts().count(),
            'banned_accounts': accounts.filter(status='banned').count(),
            'total_listings_created': sum(a.listings_created for a in accounts),
            'total_earnings': sum(float(a.total_earnings) for a in accounts),
        }

# ==========================================
# ACCOUNT HEALTH MONITOR
# ==========================================
class AccountHealthMonitor:

    class Meta:
        app_label = 'listings'

    def check_account_health(self, account):
        """Check overall health of an account."""
        health_score = 100
        issues = []
        
        if account.ban_count > 0:
            health_score -= account.ban_count * 20
            issues.append(f"⚠️ {account.ban_count} ban(s)")
        
        if account.warning_count > 0:
            health_score -= account.warning_count * 10
            issues.append(f"⚠️ {account.warning_count} warning(s)")
        
        if account.status != 'active':
            health_score -= 30
            issues.append(f"Status: {account.status}")
        
        if not account.email_verified:
            health_score -= 5
            issues.append("❌ Email not verified")
        
        return {
            'account_id': account.id,
            'health_score': max(0, health_score),
            'status': account.status,
            'issues': issues,
        }

# ==========================================
# INITIALIZE MANAGERS
# ==========================================
account_manager = AccountPoolManager()
health_monitor = AccountHealthMonitor()
