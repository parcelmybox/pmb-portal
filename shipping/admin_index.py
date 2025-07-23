from datetime import datetime, time as datetime_time, timedelta, timezone as datetime_timezone
import pytz
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.template.response import TemplateResponse
from django.db.models import Sum, Count, Q
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import Shipment, Bill
from django.db.models.functions import TruncDay

# Define UTC timezone for database operations
UTC = pytz.UTC

# Define PST timezone (handles both PST and PDT)
PACIFIC_TZ = pytz.timezone('America/Los_Angeles')

User = get_user_model()

def get_billing_stats():
    print("\n" + "="*80)
    print("=== GET_BILLING_STATS CALLED ===")
    print("="*80)
    
    try:
        from django.db.models import Sum, Count, Q, F, DecimalField
        from django.db.models.functions import Coalesce, TruncDate
        from django.db import connection
        import json
        
        # Get current time in PST
        current_time = timezone.now()
        pst_now = current_time.astimezone(PACIFIC_TZ)
        today = pst_now.date()
        
        # Calculate date ranges in PST
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        
        print(f"Current time (UTC): {current_time}")
        print(f"Current time (PST): {pst_now}")
        print(f"Current date (PST): {today}")
        print(f"Current timezone: {PACIFIC_TZ.zone}")
        print("-"*80)
        
        # Debug: Check database connection and tables
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print("\nDatabase tables:", [t[0] for t in tables])
            
            # Check if shipping_bill table exists
            cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='shipping_bill'")
            bill_table = cursor.fetchone()
            
            if bill_table:
                print("\nBill table structure:")
                cursor.execute("PRAGMA table_info(shipping_bill)")
                print([col[1] for col in cursor.fetchall()])
                
                # Get raw bill data
                cursor.execute("SELECT id, status, amount, created_at, due_date FROM shipping_bill")
                raw_bills = cursor.fetchall()
                print(f"\nFound {len(raw_bills)} raw bills in database:")
                for bill in raw_bills:
                    print(f"- ID: {bill[0]}, Status: {bill[1]}, Amount: ${bill[2]}, Created: {bill[3]}, Due: {bill[4]}")
            else:
                print("\nERROR: shipping_bill table not found in database!")
        
        # Get all bills with customer details using Django ORM
        bills = Bill.objects.all().select_related('customer')
        total_bills = bills.count()
        
        print(f"\nTotal bills via ORM: {total_bills}")
        print("All bill IDs:", [bill.id for bill in bills])
        print("All customer IDs:", [bill.customer_id for bill in bills])
        print("Unique customer IDs:", set(bill.customer_id for bill in bills))
        
        if total_bills == 0:
            print("No bills found via ORM. This might indicate a database connection issue.")
            # Try to create a test bill to verify database connection
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                test_user = User.objects.first()
                if test_user:
                    print("Creating test bill...")
                    test_bill = Bill.objects.create(
                        customer=test_user,
                        amount=100.00,
                        status='PENDING',
                        due_date=timezone.now().date() + timedelta(days=7)
                    )
                    print(f"Created test bill ID: {test_bill.id}")
                    bills = Bill.objects.all()
                    total_bills = bills.count()
            except Exception as e:
                print(f"Error creating test bill: {str(e)}")
            
            return {
                'todays_revenue': 0,
                'total_revenue': 0,
                'pending_bills': 0,
                'overdue_bills': 0,
                'revenue_change': 0,
                'pending_percentage': 0,
                'recent_bills': [],
                'total_bills': 0,
                'today': today.strftime('%b %d, %Y'),
                'debug': 'No bills found in database',
                'tables': [t[0] for t in tables] if 'tables' in locals() else []
            }
        
        # Get today's range in PST
        today_start = PACIFIC_TZ.localize(datetime.combine(today, datetime_time.min))
        today_end = today_start + timedelta(days=1)
        
        print(f"Today's range (PST): {today_start} to {today_end}")
        
        # Convert to UTC for database query
        today_start_utc = today_start.astimezone(UTC)
        today_end_utc = today_end.astimezone(UTC)
        
        print(f"Today's range (UTC): {today_start_utc} to {today_end_utc}")
        
        # Get bills created today
        today_bills = bills.filter(created_at__gte=today_start_utc, created_at__lt=today_end_utc)
        print(f"Found {today_bills.count()} bills for today")
        
        # Debug: Print the actual created_at times of bills
        print("\nBill creation times (UTC):")
        for bill in bills.order_by('-created_at')[:5]:
            print(f"- Bill {bill.id}: {bill.created_at} (PST: {bill.created_at.astimezone(PACIFIC_TZ)}), Status: {bill.status}, Amount: ${bill.amount}")
        
        # Ensure we're using Decimal for amount aggregation
        from decimal import Decimal
        today_revenue = today_bills.aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0')))['total']
        print(f"Today's revenue: ${today_revenue}")
        
        # Get yesterday's range in PST
        yesterday_start = PACIFIC_TZ.localize(datetime.combine(yesterday, datetime_time.min))
        yesterday_end = yesterday_start + timedelta(days=1)
        
        # Convert to UTC for database query
        yesterday_start_utc = yesterday_start.astimezone(UTC)
        yesterday_end_utc = yesterday_end.astimezone(UTC)
        
        # Get yesterday's revenue for comparison
        yesterday_revenue = bills.filter(
            created_at__gte=yesterday_start_utc,
            created_at__lt=yesterday_end_utc
        ).aggregate(total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0')))['total']
        
        # Calculate revenue change percentage
        revenue_change = 0
        if yesterday_revenue > 0:
            revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
        
        # Get total revenue
        total_revenue = bills.aggregate(
            total=Coalesce(Sum('amount', output_field=DecimalField()), Decimal('0')))['total']
        
        # Get pending and overdue bills
        pending_bills = bills.filter(status='PENDING').count()
        overdue_bills = bills.filter(
            Q(status='PENDING', due_date__lt=today) | 
            Q(status='OVERDUE')
        ).distinct().count()
        
        # Calculate pending percentage
        pending_percentage = (pending_bills / total_bills * 100) if total_bills > 0 else 0
        
        # Get recent bills for the table (last 10)
        recent_bills = list(bills.order_by('-created_at')[:10])
        
        # Debug: Print recent bills
        print("\nRecent Bills:")
        for bill in recent_bills:
            print(f"- ID: {bill.id}, Status: {bill.status}, Amount: ${bill.amount}, Created: {bill.created_at.astimezone(PACIFIC_TZ)}")
        
        # Get additional stats
        todays_orders = today_bills.count()
        total_customers = bills.values('customer').distinct().count()
        unpaid_bills = bills.filter(status__in=['PENDING', 'OVERDUE']).count()
        
        # Format the data for the template
        stats = {
            'todays_revenue': round(float(today_revenue), 2),
            'total_revenue': round(float(total_revenue), 2),
            'pending_bills': pending_bills,
            'overdue_bills': overdue_bills,
            'revenue_change': round(revenue_change, 2),
            'pending_percentage': round(pending_percentage, 2),
            'recent_bills': recent_bills,
            'total_bills': total_bills,
            'today': today.strftime('%b %d, %Y'),
            'todays_orders': todays_orders,
            'total_customers': total_customers,
            'unpaid_bills': unpaid_bills
        }
        
        print("\n=== BILLING STATS ===")
        print(f"Today's Revenue: ${stats['todays_revenue']}")
        print(f"Total Revenue: ${stats['total_revenue']}")
        print(f"Total Bills: {stats['total_bills']}")
        print(f"Pending Bills: {stats['pending_bills']}")
        print(f"Overdue Bills: {stats['overdue_bills']}")
        print(f"Revenue Change: {stats['revenue_change']}%")
        print(f"Pending Percentage: {stats['pending_percentage']}%")
        print(f"Today's Orders: {stats['todays_orders']}")
        print(f"Total Customers: {stats['total_customers']}")
        print(f"Unpaid Bills: {stats['unpaid_bills']}")
        print("====================\n")
        
        return stats
        
    except Exception as e:
        import traceback
        print(f"Error in get_billing_stats: {str(e)}")
        print(traceback.format_exc())
        # Return default values in case of error
        return {
            'todays_revenue': 0,
            'total_revenue': 0,
            'pending_bills': 0,
            'overdue_bills': 0,
            'revenue_change': 0,
            'pending_percentage': 0,
            'recent_bills': [],
            'total_bills': 0,
            'today': timezone.now().astimezone(PACIFIC_TZ).strftime('%b %d, %Y')
        }
        recent_bills = bills.order_by('-created_at')[:10]  # Show only 10 most recent for brevity
        print(f"Total bills in DB: {bills.count()}")
        print(f"Bill status distribution: {bills.values('status').annotate(count=Count('id')).order_by('-count')}")
        
        for bill in recent_bills:
            created_pst = bill.created_at.astimezone(PACIFIC_TZ)
            is_today = created_pst.date() == today
            is_yesterday = created_pst.date() == yesterday
            print(f"\nBill ID: {bill.id}")
            print(f"  Status: {bill.status}")
            print(f"  Amount: {bill.amount}")
            print(f"  Created (UTC): {bill.created_at}")
            print(f"  Created (PST): {created_pst}")
            print(f"  Is Paid: {bill.is_paid}")
            print(f"  Is Today: {is_today}")
            print(f"  Is Yesterday: {is_yesterday}")
            print(f"  Due Date: {getattr(bill, 'due_date', 'N/A')}")
        
        # Calculate today's revenue and orders with timezone-aware comparison
        print(f"\n=== TODAY'S BILLS (PST Date: {today}) ===")
        
        # Get today's range in PST
        today_start = PACIFIC_TZ.localize(datetime.combine(today, datetime_time.min))
        today_end = today_start + timedelta(days=1)
        
        # Convert to UTC for database query
        today_start_utc = today_start.astimezone(timezone.utc)
        today_end_utc = today_end.astimezone(timezone.utc)
        
        print(f"Today range (PST): {today_start} to {today_end}")
        print(f"Today range (UTC): {today_start_utc} to {today_end_utc}")
        
        # Get bills created today using Django ORM with timezone-aware filtering
        today_bills = bills.filter(
            created_at__gte=today_start_utc,
            created_at__lt=today_end_utc
        )
        print(f"\nFound {today_bills.count()} bills for today using ORM filtering")
        
        # Debug: Show the actual SQL query being executed
        print(f"SQL Query: {str(today_bills.query)}")
        
        # Print the bills that were found for today
        if today_bills.exists():
            print("\nToday's bills:")
            for bill in today_bills:
                created_pst = bill.created_at.astimezone(PACIFIC_TZ)
                print(f"- ID: {bill.id}, Status: {bill.status}, Amount: {bill.amount}, Created (PST): {created_pst}")
        else:
            print("No bills found for today. Checking for any bills in the database...")
            # Check if there are any bills at all
            if bills.exists():
                latest_bill = bills.latest('created_at')
                latest_pst = latest_bill.created_at.astimezone(PACIFIC_TZ)
                print(f"Latest bill in DB: ID {latest_bill.id}, Created (PST): {latest_pst}, Status: {latest_bill.status}")
            else:
                print("No bills found in the database at all.")
        
        paid_today_bills = today_bills.filter(status__iexact='PAID')  # Case-insensitive match
        print(f"Found {paid_today_bills.count()} PAID bills today")
        
        # Debug: Print all statuses in today's bills
        print("\nStatus counts in today's bills:")
        status_counts = today_bills.values('status').annotate(count=Count('id')).order_by('-count')
        for stat in status_counts:
            print(f"- {stat['status']}: {stat['count']}")
        
        today_revenue = paid_today_bills.aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total'] or 0
        today_orders = today_bills.count()
        
        print(f"Today's revenue: {today_revenue}")
        print(f"Today's orders: {today_orders}")
        
        # Calculate yesterday's revenue with timezone-aware comparison
        print(f"\n=== YESTERDAY'S BILLS (Local Date: {yesterday}) ===")
        
        # Get yesterday's range in PST
        yesterday_start = PACIFIC_TZ.localize(datetime.combine(yesterday, datetime_time.min))
        yesterday_end = yesterday_start + timedelta(days=1)
        
        # Get yesterday's bills using Django ORM with timezone-aware filtering
        yesterday_bills = bills.filter(
            created_at__gte=yesterday_start.astimezone(timezone.utc),
            created_at__lt=yesterday_end.astimezone(timezone.utc)
        )
        print(f"\nFound {yesterday_bills.count()} bills for yesterday using ORM filtering")
        
        paid_yesterday_bills = yesterday_bills.filter(status='PAID')
        print(f"Found {paid_yesterday_bills.count()} PAID bills yesterday")
        
        yesterday_revenue = paid_yesterday_bills.aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total'] or 0
        
        print(f"Yesterday's revenue: {yesterday_revenue}")
        
        # Calculate revenue change percentage
        if yesterday_revenue > 0:
            revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
        else:
            revenue_change = 100.0 if today_revenue > 0 else 0.0
        
        # Calculate order change
        yesterday_orders = yesterday_bills.count()
        order_change = ((today_orders - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else (100.0 if today_orders > 0 else 0.0)
        
        # Calculate stats
        total_revenue = bills.filter(status='PAID').aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total'] or 0
        
        # Count bills by status
        status_counts = bills.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        # Calculate pending bills (status is PENDING or DRAFT)
        pending_bills = status_dict.get('PENDING', 0) + status_dict.get('DRAFT', 0)
        
        # Calculate overdue bills
        overdue_bills = bills.filter(
            status__in=['PENDING', 'OVERDUE'],
            due_date__lt=today
        ).count()
        
        # Calculate pending percentage
        total_bills = bills.count()
        pending_percentage = round((pending_bills / total_bills * 100) if total_bills > 0 else 0, 1)
        
        # Get total number of customers
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_customers = User.objects.filter(is_staff=False).count()
        
        # Get unpaid bills (PENDING and OVERDUE statuses)
        unpaid_bills = bills.filter(status__in=['PENDING', 'OVERDUE']).count()
        
        # Prepare the result
        result = {
            'todays_revenue': float(today_revenue),
            'total_revenue': float(total_revenue),
            'pending_bills': pending_bills,
            'overdue_bills': overdue_bills,
            'todays_orders': today_orders,
            'revenue_change': round(revenue_change, 1),
            'order_change': round(order_change, 1),
            'pending_percentage': pending_percentage,
            'total_customers': total_customers,
            'unpaid_bills': unpaid_bills,
            'pending_shipments': 0  # Placeholder for future implementation
        }
        
        print("\n=== Billing Stats ===")
        for key, value in result.items():
            print(f"{key}: {value}")
        print("====================\n")
        
        return result
        
    except Exception as e:
        import traceback
        print(f"Error in get_billing_stats: {str(e)}")
        print(traceback.format_exc())
        return None
        import traceback
        traceback.print_exc()
        return None
        
    try:
        today = timezone.now().date()
        print(f"\n=== CURRENT DATE/TIME ===")
        print(f"Today's date (server time): {today}")
        print(f"Current time (server time): {timezone.now()}")
        
        # Print all unique statuses in the database first
        unique_statuses = Bill.objects.values_list('status', flat=True).distinct()
        print("\n=== UNIQUE BILL STATUSES ===")
        for status in unique_statuses:
            print(f"- {status}")
        
        # Get all bills for today with their status
        todays_bills = Bill.objects.filter(created_at__date=today)
        print(f"\n=== TODAY'S BILLS ({todays_bills.count()}) ===")
        for bill in todays_bills:
            print(f"ID: {bill.id}, Status: '{bill.status}', Amount: {bill.amount}, Created: {bill.created_at}")
        
        # Get today's revenue - be more flexible with status
        paid_statuses = ['paid', 'PAID', 'Paid', 'complete', 'COMPLETE', 'Completed']
        todays_paid_bills = Bill.objects.filter(
            created_at__date=today,
            status__in=paid_statuses
        )
        
        print(f"\n=== TODAY'S PAID BILLS: {todays_paid_bills.count()} ===")
        for bill in todays_paid_bills:
            print(f"Bill ID: {bill.id}, Status: '{bill.status}', Amount: {bill.amount}")
            
        todays_revenue = todays_paid_bills.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Get total revenue (sum of all paid bills)
        all_paid_bills = Bill.objects.filter(status__in=paid_statuses)
        print(f"\n=== ALL PAID BILLS: {all_paid_bills.count()} ===")
        for bill in all_paid_bills:
            print(f"Bill ID: {bill.id}, Status: '{bill.status}', Amount: {bill.amount}")
            
        total_revenue = all_paid_bills.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        print(f"\n=== CALCULATED REVENUE ===")
        print(f"Today's Revenue: {todays_revenue}")
        print(f"Total Revenue: {total_revenue}")
        
        # Count total customers (unique users with bills)
        total_customers = User.objects.filter(bills__isnull=False).distinct().count()
        
        # Count pending shipments (shipments not yet delivered)
        pending_shipments = Shipment.objects.exclude(status__in=['delivered', 'DELIVERED']).count()
        
        # Count unpaid bills (check various statuses that might indicate unpaid)
        unpaid_statuses = ['unpaid', 'UNPAID', 'pending', 'PENDING', 'overdue', 'OVERDUE']
        unpaid_bills = Bill.objects.filter(
            status__in=unpaid_statuses
        ).count()
        
        print(f"=== BILLS WITH UNPAID STATUSES: {unpaid_bills} ===")
        
        # Count today's orders (all bills created today)
        todays_orders = todays_bills.count()
        print(f"=== TODAY'S ORDERS: {todays_orders} ===")
        
        # Count all bills for reference
        total_bills = Bill.objects.count()
        print(f"=== TOTAL BILLS: {total_bills} ===")
        
        return {
            'total_revenue': total_revenue,
            'todays_revenue': todays_revenue,
            'total_customers': total_customers,
            'pending_shipments': pending_shipments,
            'unpaid_bills': unpaid_bills,
            'todays_orders': todays_orders,
        }
        
    except Exception as e:
        print(f"Error calculating billing stats: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    
    # Debug: Print the date range we're querying
    print(f"Today: {today}, Yesterday: {yesterday}")
    print("Querying Bill model...")
    
    # Calculate today's revenue - using 'PAID' status in uppercase
    today_revenue_qs = Bill.objects.filter(
        created_at__date=today,
        status='PAID'  # Using uppercase to match the model
    )
    today_revenue = today_revenue_qs.aggregate(total=Sum('amount'))['total'] or 0
    
    # Debug: Print today's revenue query and result
    print(f"Today's revenue query: {today_revenue_qs.query}")
    print(f"Today's revenue result: {today_revenue}")
    
    # Calculate yesterday's revenue for comparison
    yesterday_revenue_qs = Bill.objects.filter(
        created_at__date=yesterday,
        status='PAID'  # Using uppercase to match the model
    )
    yesterday_revenue = yesterday_revenue_qs.aggregate(total=Sum('amount'))['total'] or 0
    
    # Debug: Print yesterday's revenue query and result
    print(f"Yesterday's revenue query: {yesterday_revenue_qs.query}")
    print(f"Yesterday's revenue result: {yesterday_revenue}")
    
    # Calculate revenue change percentage
    if yesterday_revenue > 0:
        revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
    else:
        revenue_change = 100 if today_revenue > 0 else 0
    
    # Count today's orders (all bills created today)
    today_orders_qs = Bill.objects.filter(created_at__date=today)
    today_orders = today_orders_qs.count()
    
    # Debug: Print today's orders query and result
    print(f"Today's orders query: {today_orders_qs.query}")
    print(f"Today's orders count: {today_orders}")
    
    # Count yesterday's orders for comparison
    yesterday_orders_qs = Bill.objects.filter(created_at__date=yesterday)
    yesterday_orders = yesterday_orders_qs.count()
    orders_change = today_orders - yesterday_orders
    
    # Count total customers (non-staff users)
    total_customers = User.objects.filter(is_staff=False).count()
    
    # Count pending shipments
    pending_shipments = Shipment.objects.filter(status='PENDING').count()
    
    # Count overdue bills (PENDING with due date < today or status OVERDUE)
    overdue_bills_qs = Bill.objects.filter(
        Q(status='PENDING', due_date__lt=today) | Q(status='OVERDUE')
    )
    overdue_bills = overdue_bills_qs.count()
    
    # Debug: Print overdue bills query and result
    print(f"Overdue bills query: {overdue_bills_qs.query}")
    print(f"Overdue bills count: {overdue_bills}")
    
    # Debug: Print all bills for today with their status
    today_bills = Bill.objects.filter(created_at__date=today).values('id', 'status', 'amount', 'payment_method')
    print(f"\nToday's bills ({len(today_bills)}):")
    for bill in today_bills:
        print(f"  - Bill #{bill['id']}: Status={bill['status']}, Amount={bill['amount']}, Method={bill['payment_method']}")
    
    print("=== END BILLING STATS DEBUG ===\n")
    
    # Return the stats with keys that match the template's expectations
    return {
        'todays_revenue': float(today_revenue or 0),  # Changed from today_revenue
        'total_revenue': float(total_revenue or 0),    # Added total_revenue
        'total_customers': total_customers,
        'pending_shipments': pending_shipments,
        'unpaid_bills': overdue_bills,                 # Changed from overdue_bills
        'todays_orders': today_orders,                 # Changed from today_orders
        'revenue_change': round(revenue_change, 1),     # Keep for backward compatibility
        'order_change': orders_change                   # Keep for backward compatibility
    }

# Create a custom admin site
class CustomAdminSite(admin.AdminSite):
    site_header = 'Parcel My Box Administration'
    site_title = 'Parcel My Box Admin'
    index_title = 'Dashboard'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.index), name='index'),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        """
        Display the admin index page with billing statistics and quick links.
        """
        # Get the default context
        extra_context = extra_context or {}
        
        # Get billing stats
        billing_stats = get_billing_stats() or {}
        
        # Add default values if stats are empty
        billing_stats.setdefault('todays_revenue', 0)
        billing_stats.setdefault('total_revenue', 0)
        billing_stats.setdefault('pending_bills', 0)
        billing_stats.setdefault('overdue_bills', 0)
        billing_stats.setdefault('revenue_change', 0)
        billing_stats.setdefault('order_change', 0)
        billing_stats.setdefault('pending_percentage', 0)
        
        # Add billing stats to the context
        extra_context['billing_stats'] = billing_stats
        
        # Initialize quick links if not already set
        if 'quick_links' not in extra_context:
            extra_context['quick_links'] = []
        
        # Call the parent class's index method with our extra context
        return super().index(request, extra_context=extra_context)
    
    def each_context(self, request):
        context = super().each_context(request)
        # Add billing stats to all admin pages if needed
        if 'billing_stats' not in context:
            context['billing_stats'] = get_billing_stats()
        
        return context

# Create an instance of our custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register default admin models
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
