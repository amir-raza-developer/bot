# ==========================================
# 📡 SCHEDULE & ACCOUNT API VIEWS
# ==========================================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.utils import timezone

from .account_manager import FacebookAccount, account_manager, health_monitor
from .scheduler import ScheduledListing, scheduler_engine

# ==========================================
# SCHEDULING ENDPOINTS
# ==========================================

@csrf_exempt
def create_schedule(request):
    """Create a new schedule for listing automation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            from .models import Listing
            listing = Listing.objects.get(id=data.get('listing_id'))
            
            scheduled_time = datetime.fromisoformat(data.get('scheduled_time'))
            scheduled_time = timezone.make_aware(scheduled_time)
            
            schedule = ScheduledListing.objects.create(
                listing=listing,
                scheduled_time=scheduled_time,
                frequency=data.get('frequency', 'once'),
                num_listings=data.get('num_listings', 1),
            )
            
            if schedule.frequency != 'once':
                schedule.calculate_next_run()
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Schedule created for {scheduled_time}',
                'schedule_id': schedule.id,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'error': 'POST required'})

@csrf_exempt
def get_schedules(request):
    """Get all schedules."""
    try:
        schedules = ScheduledListing.objects.all().values(
            'id', 'listing_id', 'scheduled_time', 'frequency',
            'status', 'num_listings', 'last_run', 'next_run'
        )
        return JsonResponse({
            'success': True,
            'schedules': list(schedules)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def pause_schedule(request, schedule_id):
    """Pause a schedule."""
    try:
        schedule = ScheduledListing.objects.get(id=schedule_id)
        schedule.is_active = False
        schedule.status = 'paused'
        schedule.save()
        
        return JsonResponse({
            'success': True,
            'message': f'⏸️ Schedule {schedule_id} paused'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def resume_schedule(request, schedule_id):
    """Resume a paused schedule."""
    try:
        schedule = ScheduledListing.objects.get(id=schedule_id)
        schedule.is_active = True
        schedule.status = 'pending'
        schedule.save()
        
        return JsonResponse({
            'success': True,
            'message': f'▶️ Schedule {schedule_id} resumed'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def delete_schedule(request, schedule_id):
    """Delete a schedule."""
    try:
        schedule = ScheduledListing.objects.get(id=schedule_id)
        schedule.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'🗑️ Schedule {schedule_id} deleted'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_schedule_stats(request):
    """Get schedule statistics."""
    try:
        stats = scheduler_engine.get_schedule_stats()
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ==========================================
# ACCOUNT MANAGEMENT ENDPOINTS
# ==========================================

@csrf_exempt
def add_account(request):
    """Add new Facebook account to pool."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            account, created = account_manager.add_account(
                phone_or_email=data.get('email'),
                password=data.get('password'),
                account_name=data.get('account_name')
            )
            
            message = '✅ Account added' if created else '⚠️ Account already exists'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'account_id': account.id,
                'created': created,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'error': 'POST required'})

@csrf_exempt
def get_all_accounts(request):
    """Get all accounts in pool."""
    try:
        accounts = account_manager.get_all_accounts()
        accounts_data = [account_manager.get_account_details(a.id) for a in accounts]
        
        return JsonResponse({
            'success': True,
            'accounts': accounts_data,
            'total': len(accounts_data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_active_accounts(request):
    """Get only active accounts."""
    try:
        accounts = account_manager.get_active_accounts()
        accounts_data = [account_manager.get_account_details(a.id) for a in accounts]
        
        return JsonResponse({
            'success': True,
            'accounts': accounts_data,
            'total': len(accounts_data)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_available_account(request):
    """Get next available account for publishing."""
    try:
        account = account_manager.get_available_account()
        
        if not account:
            return JsonResponse({
                'success': False,
                'error': '❌ No available accounts'
            })
        
        return JsonResponse({
            'success': True,
            'account': account_manager.get_account_details(account.id)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_account_details(request, account_id):
    """Get details for specific account."""
    try:
        account_details = account_manager.get_account_details(account_id)
        return JsonResponse({
            'success': True,
            'account': account_details
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def update_account_status(request, account_id):
    """Update account status."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            account = FacebookAccount.objects.get(id=account_id)
            
            new_status = data.get('status')
            if new_status in dict(FacebookAccount.ACCOUNT_STATUS):
                account.status = new_status
                account.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'✅ Account status updated to {new_status}',
                    'account': account_manager.get_account_details(account_id)
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'error': 'POST required'})

@csrf_exempt
def delete_account(request, account_id):
    """Delete account from pool."""
    try:
        account = FacebookAccount.objects.get(id=account_id)
        email = account.phone_or_email
        account.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'🗑️ Account {email} deleted'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_pool_stats(request):
    """Get pool statistics."""
    try:
        stats = account_manager.get_pool_stats()
        return JsonResponse({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_account_health(request, account_id):
    """Get health status for specific account."""
    try:
        account = FacebookAccount.objects.get(id=account_id)
        health = health_monitor.check_account_health(account)
        
        return JsonResponse({
            'success': True,
            'health': health
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def rotate_account(request):
    """Rotate to next account in pool."""
    try:
        accounts = list(account_manager.get_active_accounts())
        
        if not accounts:
            return JsonResponse({
                'success': False,
                'error': '❌ No accounts in pool'
            })
        
        account = accounts[0]
        
        return JsonResponse({
            'success': True,
            'message': '➡️ Account rotated',
            'account': account_manager.get_account_details(account.id)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def get_pool_health_report(request):
    """Get health report for entire pool."""
    try:
        accounts = account_manager.get_all_accounts()
        report = {
            'total_accounts': accounts.count(),
            'accounts': [],
            'pool_average_health': 0,
        }
        
        total_health = 0
        for account in accounts:
            health = health_monitor.check_account_health(account)
            report['accounts'].append(health)
            total_health += health['health_score']
        
        if accounts.count() > 0:
            report['pool_average_health'] = total_health / accounts.count()
        
        return JsonResponse({
            'success': True,
            'report': report
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
