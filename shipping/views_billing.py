from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Sum, Count, Case, When, Value, IntegerField
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta, datetime
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth import get_user_model, login
from django.views.generic import ListView, CreateView, FormView, DeleteView, UpdateView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
import logging

# Set up logging
logger = logging.getLogger(__name__)

from .bill_models import Bill
from .activity import ActivityHistory
from .forms import BillForm, BillFilterForm
from .decorators import staff_required
from .constants import BILL_STATUS_CHOICES

User = get_user_model()

class BillListView(ListView):
    model = Bill
    template_name = 'shipping/billing/bill_list.html'
    context_object_name = 'bills'
    paginate_by = 20
    
    def get_queryset(self):
        # First, update any pending bills that are now overdue
        overdue_bills = Bill.objects.filter(
            status='PENDING',
            due_date__lt=timezone.now().date()
        )
        
        # Update status to OVERDUE for any pending bills that are now overdue
        if overdue_bills.exists():
            updated_count = overdue_bills.update(status='OVERDUE')
            if updated_count > 0:
                logger.info(f"Updated {updated_count} bills to OVERDUE status")
        
        # Get the base queryset
        queryset = Bill.objects.select_related('customer').order_by('-created_at')
        
        # Apply filters
        status = self.request.GET.get('status')
        customer_id = self.request.GET.get('customer')
        search = self.request.GET.get('search')
        
        # Handle status filter
        if status == 'OVERDUE':
            # Get pending bills that are past due date
            pending_overdue = Q(
                status='PENDING',
                due_date__lt=timezone.now().date()
            )
            # Get bills already marked as OVERDUE
            already_overdue = Q(status='OVERDUE')
            # Combine both conditions with OR
            queryset = queryset.filter(pending_overdue | already_overdue)
        elif status:
            queryset = queryset.filter(status=status)
            
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
            
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(customer__username__icontains=search) |
                Q(id__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__email__icontains=search)
            )
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the base queryset without pagination for summary
        base_queryset = self.get_queryset()
        
        # Get all bills for summary calculations
        all_bills = Bill.objects.all()
        
        # Calculate overdue bills for summary
        # Include both PENDING bills past due date and bills already marked as OVERDUE
        today = timezone.now().date()
        
        # Get bills that are PENDING and past due date
        pending_overdue = all_bills.filter(
            status='PENDING',
            due_date__lt=today
        )
        
        # Get bills already marked as OVERDUE
        already_overdue = all_bills.filter(
            status='OVERDUE'
        )
        
        # Combine both querysets and remove duplicates
        overdue_bills_qs = (pending_overdue | already_overdue).distinct()
        
        # Calculate totals
        overdue_amount = sum(bill.amount for bill in overdue_bills_qs if bill.amount is not None)
        overdue_count = overdue_bills_qs.count()
        
        # Add filter form with current request data
        context['filter_form'] = BillFilterForm(self.request.GET or None, user=self.request.user)
        
        # Get unique customers who have bills
        context['customers'] = User.objects.filter(
            id__in=all_bills.values_list('customer', flat=True).distinct()
        ).order_by('first_name', 'last_name', 'username')
        
        # Add summary data for the cards
        context['summary'] = {
            'total_bills': all_bills.count(),
            'total_amount': all_bills.aggregate(total=Sum('amount'))['total'] or 0,
            'pending_amount': all_bills.filter(status='PENDING').aggregate(total=Sum('amount'))['total'] or 0,
            'overdue_amount': overdue_amount,
            'overdue_count': overdue_count,
        }
        
        # Add current request to context for pagination
        context['request'] = self.request
        
        # Add current filters to context
        context['current_status'] = self.request.GET.get('status', '')
        context['current_customer'] = self.request.GET.get('customer', '')
        context['current_search'] = self.request.GET.get('search', '')
        
        return context

@staff_required
def create_bill(request):
    if request.method == 'POST':
        # Debug: Print form data
        print("\n=== FORM DATA ===")
        print(f"POST data: {request.POST}")
        
        form = BillForm(request.POST, user=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Debug: Print cleaned data
                    print(f"\n=== CLEANED DATA ===")
                    print(f"Status: {form.cleaned_data.get('status')}")
                    print(f"Customer input: {form.cleaned_data.get('customer_input')}")
                    
                    bill = form.save(commit=False)
                    bill.created_by = request.user
                    
                    # Debug: Print bill status before any changes
                    print(f"\n=== BILL STATUS ===")
                    print(f"Before setting customer - Status: {bill.status}")
                    
                    # Handle customer input
                    customer_input = form.cleaned_data.get('customer_input', '').strip()
                    
                    # Try to find existing user by email or username
                    user = User.objects.filter(
                        Q(email__iexact=customer_input) | 
                        Q(username__iexact=customer_input) |
                        Q(first_name__iexact=customer_input)
                    ).first()
                    
                    if not user and customer_input:  # Create new user if not found
                        username = customer_input.lower().replace(' ', '_')
                        email = f"{username}@example.com" if '@' not in customer_input else customer_input
                        
                        # Generate a random password
                        password = get_random_string(12)
                        user = User.objects.create_user(
                            username=username,
                            email=email,
                            first_name=customer_input,
                            is_active=False,  # Mark as inactive until verified
                            password=password
                        )
                    
                    bill.customer = user
                    
                    # Debug: Print bill status after setting customer
                    print(f"After setting customer - Status: {bill.status}")
                    
                    # Set default due date to 10 days from now if not provided
                    if not bill.due_date:
                        bill.due_date = timezone.now().date() + timedelta(days=10)
                        
                    # Debug: Print payment method before saving
                    print(f"Payment method before save: {bill.payment_method}")
                    print(f"Form payment method: {form.cleaned_data.get('payment_method')}")
                    
                    # Debug: Print before setting paid_at
                    print(f"Before setting paid_at - Status: {bill.status}, paid_at: {bill.paid_at}")
                    
                    # Ensure payment method is set from form data
                    if 'payment_method' in form.cleaned_data:
                        bill.payment_method = form.cleaned_data['payment_method']
                        print(f"Set payment method to: {bill.payment_method}")
                    
                    # Set paid_at timestamp if status is PAID
                    if bill.status == 'PAID' and not bill.paid_at:
                        bill.paid_at = timezone.now()
                        print(f"Set paid_at to: {bill.paid_at}")
                    
                    # Debug: Print before save
                    print(f"Before save - Status: {bill.status}, paid_at: {bill.paid_at}")
                    
                    bill.save()
                    
                    # Debug: Print after save
                    print(f"After save - Status: {bill.status}, paid_at: {bill.paid_at}")
                    print(f"Bill ID: {bill.id}")
                    
                    # Log the bill generation
                    ActivityHistory.log_activity(
                        user=request.user,
                        action='Bill Generated',
                        obj=bill
                    )
                    
                    messages.success(request, f'Bill #{bill.id} has been generated successfully.')
                    return redirect('shipping:bill_detail', bill_id=bill.id)
                    
            except Exception as e:
                messages.error(request, f'Error generating bill: {str(e)}')
                # Log the error
                logger.error(f'Error generating bill: {str(e)}', exc_info=True)
    else:
        initial_data = {}
        customer_id = request.GET.get('customer_id')
        if customer_id:
            try:
                customer = User.objects.get(id=customer_id, is_staff=False)
                initial_data['customer_input'] = customer.get_full_name() or customer.username
            except User.DoesNotExist:
                pass
                
        form = BillForm(initial=initial_data, user=request.user)
    
    # Get active customers for the dropdown
    customers = User.objects.filter(is_active=True, is_staff=False).order_by('first_name', 'last_name', 'username')
    
    context = {
        'form': form,
        'customers': customers,
        'title': 'Generate New Bill'
    }
    
    return render(request, 'shipping/billing/create_bill.html', context)

@staff_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Check if the user has permission to view this bill
    if not request.user.is_staff and request.user != bill.customer:
        messages.error(request, 'You do not have permission to view this bill.')
        return redirect('shipping:bill_list')
    
    # Get related bills for the same customer
    related_bills = Bill.objects.filter(customer=bill.customer).exclude(id=bill.id).order_by('-created_at')[:5]
    
    # Get customer statistics
    customer_stats = Bill.objects.filter(customer=bill.customer).aggregate(
        total_bills=Count('id'),
        total_paid=Sum('amount', filter=Q(status='PAID')),
        total_pending=Sum('amount', filter=Q(status='PENDING') | Q(status='OVERDUE')),
    )
    
    # Get activity history for this bill
    activity_history = ActivityHistory.objects.filter(
        content_type__model='bill',
        object_id=bill.id
    ).select_related('user').order_by('-timestamp')
    
    return render(request, 'shipping/billing/bill_detail.html', {
        'bill': bill,
        'related_bills': related_bills,
        'customer_stats': customer_stats,
        'activity_history': activity_history,
        'now': timezone.now(),  # Add current time for cache busting
    })

def export_bill_pdf(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Check permissions
    if not request.user.is_staff and bill.customer != request.user:
        messages.error(request, "You don't have permission to view this bill.")
        return redirect('shipping:bill_list')
    
    # Get the template
    template = get_template('shipping/billing/bill_pdf_clean.html')
    
    # Prepare context
    now = timezone.now()
    context = {
        'bill': bill,
        'company_name': 'ParcelMyBox',
        'company_address': '123 Business Street, City, Country',
        'company_phone': '(123) 456-7890',
        'company_email': 'billing@parcelmybox.com',
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': str(settings.STATIC_ROOT).replace('\\', '/'),  # Convert Windows paths to forward slashes
        'today': now.date(),
        'now': now,  # Add current datetime for template debugging
        'request': request  # Add request to context for absolute URLs
    }
    
    # Render the HTML
    html = template.render(context)
    
    # Create a file-like buffer to receive PDF data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{bill.id}.pdf"'
    
    # Generate PDF
    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        encoding='UTF-8',
    )
    
    # If error, show error message
    if pisa_status.err:
        messages.error(request, 'Error generating PDF. Please try again.')
        return redirect('shipping:bill_detail', bill_id=bill.id)
    
    return response

@staff_required
def update_bill_status(request, bill_id):
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        bill = get_object_or_404(Bill, id=bill_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(BILL_STATUS_CHOICES).keys():
            old_status = bill.status
            bill.update_status(new_status)
            
            # Log the status change
            ActivityHistory.objects.create(
                user=request.user,
                action=f'Bill status changed from {old_status} to {new_status}',
                content_object=bill,
                extra_data={
                    'old_status': old_status,
                    'new_status': new_status,
                    'bill_id': bill.id,
                    'amount': str(bill.amount)
                }
            )
            
            return JsonResponse({'success': True, 'new_status': bill.get_status_display()})
        
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def delete_bill(request, bill_id):
    """
    View to delete a bill. Only accessible by staff members.
    """
    if not request.user.is_staff:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        messages.error(request, 'You do not have permission to delete bills.')
        return redirect('shipping:bill_list')
    
    bill = get_object_or_404(Bill, id=bill_id)
    
    if request.method == 'POST':
        try:
            # Log the deletion before actually deleting
            ActivityHistory.objects.create(
                user=request.user,
                action=f'Bill #{bill.id} deleted (Customer: {bill.customer}, Amount: ${bill.amount}, Status: {bill.status})',
                content_object=None  # No content object since we're deleting it
            )
            
            # Delete the bill
            bill.delete()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
                
            messages.success(request, 'Bill has been deleted successfully.')
            return redirect('shipping:bill_list')
            
        except Exception as e:
            logger.error(f"Error deleting bill {bill_id}: {str(e)}")
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
            messages.error(request, f'Error deleting bill: {str(e)}')
            return redirect('shipping:bill_detail', bill_id=bill_id)
    
    # If not a POST request, show confirmation page
    return render(request, 'shipping/billing/bill_confirm_delete.html', {'bill': bill})


def edit_bill(request, bill_id):
    """
    View to edit an existing bill. Only accessible by staff members.
    """
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to edit bills.')
        return redirect('shipping:bill_list')
    
    bill = get_object_or_404(Bill, id=bill_id)
    
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_bill = form.save(commit=False)
                    
                    # Handle customer input
                    customer_input = form.cleaned_data.get('customer_input', '').strip()
                    print(f"\n=== CUSTOMER INPUT ===")
                    print(f"Raw customer input: {customer_input}")
                    print(f"Current customer: {updated_bill.customer.get_full_name()} (ID: {updated_bill.customer_id})")
                    
                    if customer_input:
                        # Try to find existing user by email, username, or name
                        user = User.objects.filter(
                            Q(email__iexact=customer_input) | 
                            Q(username__iexact=customer_input) |
                            Q(first_name__iexact=customer_input) |
                            Q(last_name__iexact=customer_input) |
                            Q(first_name__iexact=' '.join(customer_input.split()[:-1]), 
                              last_name__iexact=customer_input.split()[-1] if ' ' in customer_input else '') |
                            Q(first_name__iexact=customer_input.split()[0], 
                              last_name__iexact=' '.join(customer_input.split()[1:]) if len(customer_input.split()) > 1 else '')
                        ).first()
                        
                        if user:
                            print(f"Found user: {user.get_full_name()} (ID: {user.id})")
                            updated_bill.customer = user
                            print(f"Updated bill customer to: {updated_bill.customer.get_full_name()} (ID: {updated_bill.customer_id})")
                        else:
                            print("No matching user found, keeping existing customer")
                            print(f"Current customer remains: {updated_bill.customer.get_full_name()} (ID: {updated_bill.customer_id})")
                    
                    # Save the bill with updated fields
                    updated_bill.save()
                    
                    # Log the update
                    ActivityHistory.objects.create(
                        user=request.user,
                        action=f'Bill #{bill.id} updated',
                        content_object=bill
                    )
                    
                    messages.success(request, f'Bill #{bill.id} has been updated successfully.')
                    print(f"Successfully updated bill #{bill.id}")
                    return redirect('shipping:bill_detail', bill_id=bill.id)
                    
            except Exception as e:
                logger.error(f"Error updating bill {bill_id}: {str(e)}")
                messages.error(request, f'Error updating bill: {str(e)}')
    else:
        # Initialize form with bill data
        initial_data = {
            'customer_input': bill.customer.get_full_name() or bill.customer.username,
            'amount': bill.amount,
            'status': bill.status,
            'due_date': bill.due_date,
            'description': bill.description
        }
        form = BillForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'bill': bill,
        'title': f'Edit Bill #{bill.id}'
    }
    return render(request, 'shipping/billing/create_bill.html', context)
