from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.template.response import TemplateResponse
from django.db.models import Sum, Count, Q
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import Shipment
# Import Bill model with absolute import to avoid circular imports
from shipping.bill_models import Bill

User = get_user_model()

def get_billing_stats():
    print("\n" + "="*50)
    print("=== GET_BILLING_STATS CALLED ===")
    print("="*50)
    print("Current time:", timezone.now())
    print("="*50)
    
    # Debug: Check if Bill model is imported correctly
    print(f"Bill model: {Bill}")
    print(f"Bill model __module__: {Bill.__module__}")
    print(f"Bill model __name__: {Bill.__name__}")
    
    # Debug: Verify the database connection and table
    from django.db import connection
    print(f"Database connection: {connection.settings_dict['NAME']}")
    
    # Debug: List all tables in the database
    tables = connection.introspection.table_names()
    print(f"Database tables: {tables}")
    
    # Debug: Check if the bills table exists
    bill_table_name = Bill._meta.db_table
    print(f"Looking for bill table: {bill_table_name}")
    
    if bill_table_name not in tables:
        print(f"ERROR: Table {bill_table_name} not found in database!")
        return None
    
    # Debug: Check if there are any bills in the database
    try:
        bill_count = Bill.objects.count()
        print(f"Total bills in database: {bill_count}")
        
        # Print first few bills for debugging
        if bill_count > 0:
            print("Sample bills:")
            for bill in Bill.objects.all()[:3]:
                print(f"- ID: {bill.id}, Amount: {bill.amount}, Status: {bill.status}, Created: {bill.created_at}")
    except Exception as e:
        print(f"Error counting bills: {e}")
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
        Display the admin index page with billing statistics.
        """
        # Get the default context
        context = {}
        context.update(admin.site.each_context(request))
        
        # Add billing stats to the context
        billing_stats = get_billing_stats()
        if billing_stats:
            context['billing_stats'] = billing_stats
        
        # Add app list to the context
        app_list = self.get_app_list(request)
        context.update({
            'title': 'Dashboard',
            'app_list': app_list,
            'has_permission': self.has_permission(request),
            'is_popup': False,
            'is_nav_sidebar_enabled': self.enable_nav_sidebar,
            'available_apps': app_list,
            **(extra_context or {}),
        })
        
        # Use the custom template
        return TemplateResponse(request, 'admin/index.html', context)
    
    def each_context(self, request):
        context = super().each_context(request)
        # Add billing stats to all admin pages if needed
        if 'billing_stats' not in context:
            context['billing_stats'] = get_billing_stats()
        
        return context

# Create an instance of our custom admin site
custom_admin_site = CustomAdminSite()
