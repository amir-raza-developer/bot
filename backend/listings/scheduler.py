# ==========================================
# ⏰ SCHEDULING SYSTEM MODULE
# ==========================================

from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import pytz

# ==========================================
# SCHEDULE MODEL
# ==========================================
class ScheduledListing(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
    ]
    
    listing = models.ForeignKey('listings.Listing', on_delete=models.CASCADE, related_name='schedules')
    scheduled_time = models.DateTimeField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once')
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    num_listings = models.IntegerField(default=1)
    
    # Timing info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    class Meta:
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"Schedule {self.id} - {self.frequency} - {self.status}"
    
    def is_ready_to_run(self):
        """Check if schedule should run now."""
        if not self.is_active or self.status == 'paused':
            return False
        
        now = timezone.now()
        if self.scheduled_time <= now:
            return True
        return False
    
    def calculate_next_run(self):
        """Calculate next run time based on frequency."""
        last = self.last_run or self.scheduled_time
        
        if self.frequency == 'daily':
            self.next_run = last + timedelta(days=1)
        elif self.frequency == 'weekly':
            self.next_run = last + timedelta(weeks=1)
        elif self.frequency == 'monthly':
            self.next_run = last + timedelta(days=30)
        else:
            self.next_run = None
        
        self.save()

# ==========================================
# SCHEDULER ENGINE
# ==========================================
class SchedulerEngine:
    def __init__(self):
        self.running_schedules = []
        self.completed_schedules = []

    def get_pending_schedules(self):
        """Get all schedules ready to run."""
        now = timezone.now()
        return ScheduledListing.objects.filter(
            scheduled_time__lte=now,
            is_active=True,
            status='pending'
        ).order_by('scheduled_time')

    def update_schedule_status(self, schedule, status, error_msg=None):
        """Update schedule status."""
        schedule.status = status
        schedule.last_run = timezone.now()
        
        if error_msg:
            schedule.error_message = error_msg
            schedule.retry_count += 1
        
        if status == 'completed':
            schedule.calculate_next_run()
        
        schedule.save()
        return schedule

    def get_schedule_stats(self):
        """Get statistics about schedules."""
        return {
            'total': ScheduledListing.objects.count(),
            'pending': ScheduledListing.objects.filter(status='pending').count(),
            'running': ScheduledListing.objects.filter(status='running').count(),
            'completed': ScheduledListing.objects.filter(status='completed').count(),
            'failed': ScheduledListing.objects.filter(status='failed').count(),
        }

# ==========================================
# INITIALIZE SCHEDULER
# ==========================================
scheduler_engine = SchedulerEngine()
