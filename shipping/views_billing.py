from decimal import Decimal
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

from .models import Bill
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
        # Update PENDING bills that are now overdue
        overdue_bills = Bill.objects.filter(
            status='PENDING',
            due_date__lt=timezone.now().date()
        )
        if overdue_bills.exists():
            updated_count = overdue_bills.update(status='OVERDUE')
            if updated_count > 0:
                logger.info(f"Updated {updated_count} bills to OVERDUE status")

        queryset = Bill.objects.select_related('customer').order_by('-created_at')

        # Filters
        status = self.request.GET.get('status')
        customer_id = self.request.GET.get('customer')
        search = self.request.GET.get('search')

        if status == 'OVERDUE':
            # Bills that are overdue (either marked or past due date)
            pending_overdue = Q(status='PENDING', due_date__lt=timezone.now().date())
            already_overdue = Q(status='OVERDUE')
            queryset = queryset.filter(pending_overdue | already_overdue)
        elif status:
            queryset = queryset.filter(status=status)

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        if search:
            queryset = queryset.filter(
                Q(phone_number__icontains=search) |
                Q(customer__username__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__email__icontains=search) |
                Q(id__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_bills = Bill.objects.select_related('customer')

        today = timezone.now().date()
        pending_overdue = all_bills.filter(status='PENDING', due_date__lt=today)
        already_overdue = all_bills.filter(status='OVERDUE')
        overdue_bills_qs = (pending_overdue | already_overdue).distinct()

        overdue_amount = sum(bill.total for bill in overdue_bills_qs)
        overdue_count = overdue_bills_qs.count()

        context['filter_form'] = BillFilterForm(self.request.GET or None, user=self.request.user)

        context['customers'] = User.objects.filter(
            id__in=all_bills.values_list('customer', flat=True).distinct()
        ).order_by('first_name', 'last_name', 'username')

        context['summary'] = {
            'total_bills': all_bills.count(),
            'total_amount': sum(bill.total for bill in all_bills),
            'pending_amount': sum(bill.total for bill in all_bills.filter(status='PENDING')),
            'overdue_amount': overdue_amount,
            'overdue_count': overdue_count,
        }

        context['request'] = self.request
        context['current_status'] = self.request.GET.get('status', '')
        context['current_customer'] = self.request.GET.get('customer', '')
        context['current_search'] = self.request.GET.get('search', '')

        return context

@staff_required
def create_bill(request):
    if request.method == 'POST':
        form = BillForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    bill = form.save(commit=False)

                    # Set created_by to the logged-in user
                    bill.created_by = request.user

                    # Set billed_weight as rounded weight
                    bill.billed_weight = round(bill.weight)

                    bill.save()

                    messages.success(request, f'Bill #{bill.id} created successfully.')
                    return redirect('shipping:bill_detail', bill_id=bill.id)

            except Exception as e:
                messages.error(request, f"Error generating bill: {str(e)}")

    else:
        form = BillForm()

    context = {
        'form': form,
        'title': 'Generate New Bill',
        'submit_text': 'Create Bill',
        'cancel_url': reverse('shipping:bill_list')
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
    bills = Bill.objects.filter(customer=bill.customer)
    customer_stats = {
        'total_bills': bills.count(),
        'total_paid': sum(b.total for b in bills if b.status == 'PAID'),
        'total_pending': sum(b.total for b in bills if b.status in ['PENDING', 'OVERDUE']),
    }
    
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
    
    # Use the simple template
    template_path = 'shipping/billing/bill_pdf_simple.html'
    template = get_template(template_path)
    
    # Prepare company information
    company_info = {
        'name': 'ParcelMyBox',
        'address': '123 Business Street, San Francisco, CA 94105',
        'phone': '+1 (415) 555-0123',
        'email': 'billing@parcelmybox.com',
        'website': 'www.parcelmybox.com',
        'tax_id': 'TAX-123-456-789',
    }
    
    # Calculate totals if not already set
    subtotal = bill.amount or 0
    tax_rate = Decimal('0.10')  # 10% tax rate as an example
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    # Calculate due date if not set
    due_date = bill.due_date or (timezone.now() + timedelta(days=15)).date()
    
    # Get bill items safely
    items = []
    if hasattr(bill, 'items') and hasattr(bill.items, 'all'):
        try:
            items = list(bill.items.all())
        except (AttributeError, TypeError):
            items = []
    
    # If no items, create a default item from the bill
    if not items and bill.amount:
        items = [{
            'description': bill.description or 'Shipping Service',
            'quantity': 1,
            'unit_price': bill.amount,
            'total': bill.amount
        }]
    
    # Prepare context
    now = timezone.now()
    context = {
        'bill': bill,
        'company_name': company_info['name'],
        'company_address': company_info['address'],
        'company_phone': company_info['phone'],
        'company_email': company_info['email'],
        'company_website': company_info['website'],
        'company_tax_id': company_info['tax_id'],
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': str(settings.STATIC_ROOT).replace('\\', '/'),
        'today': now.date(),
        'due_date': due_date,
        'now': now,
        'request': request,
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'tax_rate': tax_rate * 100,  # Convert to percentage
        'total': total,
        'payment_terms': 'Net 15',
        'items': items
    }
    
    # Render the HTML with context
    html = template.render(context)
    
    # Create HTTP response with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{bill.id}.pdf"'
    
    try:
        # Generate PDF using xhtml2pdf with minimal configuration
        from xhtml2pdf import pisa
        
        # Simple CSS to ensure basic formatting
        default_css = """
            body {
                font-family: Arial, sans-serif;
                font-size: 10px;
                line-height: 1.4;
                margin: 0;
                padding: 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 6px;
                text-align: left;
            }
            th {
                background-color: #f5f5f5;
                font-weight: bold;
            }
        """
        
        # Generate PDF
        pisa_status = pisa.CreatePDF(
            html,
            dest=response,
            encoding='UTF-8',
            link_callback=None,
            show_error_as_pdf=False,
            xhtml=False,
            default_css=default_css
        )
        
        # Check for errors
        if pisa_status.err:
            logger.error(f'PDF generation error: {pisa_status.err}')
            messages.error(request, 'Error generating PDF. Please try again.')
            return redirect('shipping:bill_detail', bill_id=bill.id)
            
    except Exception as e:
        logger.error(f'Error in PDF generation: {str(e)}')
        messages.error(request, f'Error generating PDF: {str(e)}')
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
    
    # Get the bill with customer data
    bill = get_object_or_404(Bill.objects.select_related('customer'), id=bill_id)
    
    if request.method == 'POST':
        # Create a mutable copy of POST data
        post_data = request.POST.copy()
        
        # Get the customer name from the form data
        customer_name = post_data.get('customer_name', '').strip()
        
        # If customer name is provided, update the form data
        if customer_name:
            # Set the customer_id to empty to force the form to handle the customer name
            post_data['customer_id'] = ''
        
        form = BillForm(post_data, instance=bill, user=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_bill = form.save(commit=False)
                    
                    # Debug: Print customer information
                    print("\n=== CUSTOMER INFO ===")
                    print(f"Customer name from form: {form.cleaned_data.get('customer_name')}")
                    print(f"Current customer: {updated_bill.customer} (ID: {updated_bill.customer_id})")
                    
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
            'customer_name': bill.customer.get_full_name() or bill.customer.username,
            'customer_id': bill.customer_id,
            'amount': bill.amount,
            'status': bill.status,
            'due_date': bill.due_date,
            'description': bill.description,
            'package': bill.package,
            'weight': bill.weight,
            'courier_service': bill.courier_service,
            'payment_method': bill.payment_method
        }
        form = BillForm(initial=initial_data, user=request_user)
    
    context = {
        'form': form,
        'bill': bill,
        'title': f'Edit Bill #{bill.id}'
    }
    return render(request, 'shipping/billing/create_bill.html', context)
