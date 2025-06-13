from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.utils import timezone
import requests
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

@staff_member_required
def billing_dashboard(request):
    try:
        # Fetch data from the billing API
        api_url = 'http://127.0.0.1:8000/shipping/bills/'
        print(f"\n=== DEBUG: Fetching bills from {api_url} ===")
        
        # Add headers to request JSON response
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
        
        # Add format=json parameter to ensure JSON response
        params = {'format': 'json'}
        
        response = requests.get(api_url, headers=headers, params=params)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            error_msg = f'Failed to fetch billing data: {response.status_code} - {response.text}'
            print(f"ERROR: {error_msg}")
            return JsonResponse({'error': error_msg}, status=500)
            
        bills = response.json()
        
        # Debug: Print the raw bills data
        print("\n" + "="*50)
        print("=== DEBUG: RAW BILLS DATA ===")
        print(f"Number of bills: {len(bills)}")
        if bills:
            print("\nSample bill structure:")
            for i, bill in enumerate(bills[:3]):  # Show first 3 bills
                print(f"\nBill #{i+1}:")
                for key, value in bill.items():
                    print(f"  {key}: {value} (type: {type(value)})")
        print("\n" + "="*50 + "\n")
        
        # Get current date and calculate date ranges
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        this_month = today.replace(day=1)
        
        # Debug: Print the dates we're using
        print(f"\n=== DEBUG: Date Info ===")
        print(f"Today: {today}")
        print(f"Yesterday: {yesterday}")
        print("=========================\n")
        
        # Enhanced date parsing function
        def parse_date(date_str):
            if not date_str:
                return None
                
            # Handle datetime objects directly
            if hasattr(date_str, 'date'):
                return date_str.date() if hasattr(date_str, 'date') else date_str
                
            # Convert to string if not already
            date_str = str(date_str)
            
            # Try different date formats
            date_formats = [
                '%Y-%m-%d',  # 2023-06-11
                '%Y-%m-%dT%H:%M:%S',  # ISO format with time
                '%Y-%m-%d %H:%M:%S',  # MySQL datetime format
                '%Y-%m-%dT%H:%M:%S.%fZ',  # ISO format with microseconds and Z
                '%Y-%m-%dT%H:%M:%S%z',  # ISO format with timezone
                '%d/%m/%Y',  # 11/06/2023
                '%m/%d/%Y',  # 06/11/2023
                '%d-%m-%Y',  # 11-06-2023
                '%m-%d-%Y',  # 06-11-2023
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # Convert to date object for consistent comparison
                    return dt.date() if hasattr(dt, 'date') else dt
                except (ValueError, TypeError):
                    continue
            
            print(f"Warning: Could not parse date: {date_str}")
            return None
                
        # Process bills
        total_bills = 0
        pending_bills = []
        paid_bills = []
        overdue_bills = []
        today_orders = 0
        total_revenue = 0
        today_revenue = 0
        
        print("\n" + "="*50)
        print("=== DEBUG: PROCESSING BILLS ===")
        print(f"Current date: {today}")
        print("-"*50)
        
        print("\n=== DEBUG: Processing Bills ===")
        
        for bill in bills:
            # Get bill data with defaults
            bill_id = bill.get('id', 'unknown')
            amount = float(bill.get('amount', 0))
            status = str(bill.get('status', '')).lower()
            created_at = bill.get('created_at')
            due_date = bill.get('due_date')
            
            print(f"\nProcessing Bill ID: {bill_id}")
            print(f"- Status: {status}")
            print(f"- Amount: {amount}")
            print(f"- Created At: {created_at}")
            print(f"- Due Date: {due_date}")
            
            try:
                # Count all bills
                total_bills += 1
                total_revenue += float(amount) if amount else 0
                
                # Get payment method
                payment_method = bill.get('payment_method', 'CASH')
                
                print(f"\nProcessing Bill ID: {bill_id}")
                print(f"- Status: {status}")
                print(f"- Amount: {amount} (type: {type(amount)})")
                print(f"- Payment Method: {payment_method}")
                print(f"- Created At: {created_at} (type: {type(created_at)})")
                print(f"- Due Date: {due_date} (type: {type(due_date)})")
                
                # Categorize by status
                if status == 'pending':
                    pending_bills.append(bill)
                    print("- Added to pending bills")
                elif status == 'paid':
                    paid_bills.append(bill)
                    print("- Added to paid bills")
                else:
                    print(f"- Unknown status: {status}")
                    
            except Exception as e:
                print(f"ERROR processing bill {bill_id}: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Check for overdue bills
            if status == 'pending' and due_date:
                due = parse_date(due_date)
                print(f"- Due date parsed: {due}")
                if due:
                    if due < today:
                        overdue_bills.append(bill)
                        print(f"- Added to overdue bills (due: {due} < today: {today})")
            
            # Count today's orders
            if created_at:
                created = parse_date(created_at)
                print(f"- Created date parsed: {created} (type: {type(created)})")
                print(f"- Today's date: {today} (type: {type(today)})")
                if created:
                    # Convert both dates to string for comparison to avoid timezone issues
                    created_str = created.strftime('%Y-%m-%d') if hasattr(created, 'strftime') else str(created)
                    today_str = today.strftime('%Y-%m-%d') if hasattr(today, 'strftime') else str(today)
                    
                    print(f"- Comparing dates - Created: {created_str}, Today: {today_str}")
                    
                    if created_str == today_str:
                        today_orders += 1
                        today_revenue += amount
                        print(f"- Added to today's orders (created: {created_str} == today: {today_str})")
                    else:
                        print(f"- Not today's order (created: {created_str} != today: {today_str})")
            else:
                print("- No created_at date found")
        
        print("\n" + "="*50)
        print("=== DEBUG: FINAL STATS ===")
        print(f"Total bills processed: {total_bills}")
        print(f"Pending bills: {len(pending_bills)}")
        print(f"Paid bills: {len(paid_bills)}")
        print(f"Overdue bills: {len(overdue_bills)}")
        print(f"Today's orders: {today_orders}")
        print(f"Today's revenue: ${today_revenue:.2f}")
        print(f"Total revenue: ${total_revenue:.2f}")
        print("\nContext being passed to template:")
        print({
            'total_bills': total_bills,
            'pending_bills': len(pending_bills),
            'paid_bills': len(paid_bills),
            'overdue_bills': len(overdue_bills),
            'today_orders': today_orders,
            'today_revenue': today_revenue,
            'total_revenue': total_revenue
        })
        print("="*50 + "\n")
        
        # Calculate statistics
        pending_count = len(pending_bills)
        paid_count = len(paid_bills)
        overdue_count = len(overdue_bills)
        
        # Calculate percentages
        pending_percentage = round((pending_count / total_bills * 100) if total_bills > 0 else 0, 1)
        paid_percentage = round((paid_count / total_bills * 100) if total_bills > 0 else 0, 1)
        
        # Calculate revenue change (compared to yesterday)
        yesterday_revenue = 0
        yesterday_orders = 0
        for bill in bills:
            created_at = bill.get('created_at')
            if created_at:
                created = parse_date(created_at)
                if created == yesterday:
                    if bill.get('status', '').lower() == 'paid':
                        yesterday_revenue += float(bill.get('amount', 0))
                    yesterday_orders += 1
        
        # Calculate order change
        order_change = today_orders - yesterday_orders if yesterday_orders > 0 else today_orders
        
        # Calculate revenue change percentage
        if yesterday_revenue > 0:
            revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
        else:
            revenue_change = 100.0 if today_revenue > 0 else 0.0
        
        # Get recent bills (last 5)
        recent_bills = sorted(bills, 
                            key=lambda x: x.get('created_at', ''), 
                            reverse=True)[:5]
        
        # Prepare context with all required variables
        context = {
            # Bill counts
            'total_bills': total_bills,
            'pending_bills': pending_count,  # Using count instead of list
            'paid_bills': paid_count,        # Using count instead of list
            'overdue_bills': overdue_count,  # Using count instead of list
            
            # Today's stats
            'today_orders': today_orders,
            'today_revenue': today_revenue,
            'total_revenue': total_revenue,
            
            # Percentages
            'pending_percentage': pending_percentage,
            'paid_percentage': paid_percentage,
            'revenue_change': revenue_change,
            'order_change': order_change,
            
            # Other data
            'recent_bills': recent_bills,
            'has_permission': True,
            'today': today.strftime('%Y-%m-%d'),
        }
        
        return render(request, 'admin/billing_dashboard.html', context)
        
    except Exception as e:
        import traceback
        print(f"Error in billing_dashboard: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({'error': str(e)}, status=500)
