from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from pytz import timezone as pytz_timezone
from .models import Bill

PACIFIC_TZ = pytz_timezone('America/Los_Angeles')

def debug_user(request):
    """
    Debug view to display current user information.
    """
    user = request.user
    data = {
        'is_authenticated': user.is_authenticated,
        'username': user.username if user.is_authenticated else 'Anonymous',
        'is_staff': user.is_staff if user.is_authenticated else False,
        'is_superuser': user.is_superuser if user.is_authenticated else False,
        'permissions': list(user.get_all_permissions()) if user.is_authenticated else [],
    }
    return JsonResponse(data)

@login_required
def protected_debug(request):
    """
    A protected debug view that requires login.
    """
    return JsonResponse({
        'status': 'success',
        'message': f'You are logged in as {request.user.username}',
        'is_staff': request.user.is_staff,
        'is_superuser': request.user.is_superuser
    })

def debug_billing_stats(request):
    """Debug view to display billing statistics and bill details"""
    now = timezone.now()
    now_pst = now.astimezone(PACIFIC_TZ)
    today = now_pst.date()
    
    # Get all bills ordered by creation date
    all_bills = Bill.objects.all().order_by('created_at')
    
    # Get today's bills (PST timezone)
    today_bills = [
        bill for bill in all_bills 
        if bill.created_at.astimezone(PACIFIC_TZ).date() == today
    ]
    
    # Calculate today's revenue
    today_revenue = sum(float(bill.amount) for bill in today_bills if bill.status == 'PAID')
    
    # Prepare bill details
    bill_details = []
    for bill in all_bills:
        created_pst = bill.created_at.astimezone(PACIFIC_TZ)
        bill_details.append({
            'id': bill.id,
            'created_utc': bill.created_at,
            'created_pst': created_pst,
            'status': bill.status,
            'amount': float(bill.amount) if bill.amount else 0.0,
            'is_today': created_pst.date() == today,
            'is_paid': bill.status == 'PAID'
        })
    
    context = {
        'current_time_utc': now,
        'current_time_pst': now_pst,
        'today': today,
        'total_bills': all_bills.count(),
        'today_bills_count': len(today_bills),
        'today_revenue': today_revenue,
        'bills': bill_details,
    }
    
    return render(request, 'shipping/debug_billing.html', context)
