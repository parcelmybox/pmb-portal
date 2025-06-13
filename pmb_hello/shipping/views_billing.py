from datetime import datetime, timedelta
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Sum, Count, F, Value, Case, When, IntegerField
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.conf import settings

from .models import Bill, ActivityHistory, User
from .forms import BillForm, BillFilterForm

# Set up logging
logger = logging.getLogger(__name__)

# Get user model
User = get_user_model()

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/')
def create_bill(request):
    """
    View for creating a new bill.
    """
    initial = {}
    customer_id = request.GET.get('customer_id')
    
    if customer_id:
        try:
            customer = User.objects.get(id=customer_id, is_active=True)
            initial['customer'] = customer
        except User.DoesNotExist:
            messages.warning(request, 'The specified customer was not found.')
    
    if request.method == 'POST':
        form = BillForm(request.POST, request=request)
        
        if form.is_valid():
            # Create the bill
            bill = form.save(commit=False)
            bill.created_by = request.user
            bill.save()
            
            # Log the activity
            ActivityHistory.objects.create(
                user=request.user,
                activity_type='BILL_GENERATED',
                description=f'Generated bill #{bill.id} for {bill.customer.get_full_name() or bill.customer.username} - ${bill.amount:,.2f}',
                reference_id=bill.id,
                reference_model='Bill',
                metadata={
                    'amount': str(bill.amount),
                    'customer_id': bill.customer.id,
                    'due_date': bill.due_date.isoformat() if bill.due_date else None
                }
            )
            
            messages.success(
                request,
                f'Bill #{bill.id} for {bill.customer.get_full_name() or bill.customer.username} has been created successfully.'
            )
            
            # Redirect based on the 'save_and_add_another' button
            if 'save_and_add_another' in request.POST:
                return redirect('shipping:create_bill')
            return redirect('shipping:bill_detail', bill_id=bill.id)
    else:
        form = BillForm(initial=initial, request=request)
    
    context = {
        'form': form,
        'title': 'Create New Bill',
        'submit_text': 'Create Bill',
        'cancel_url': 'shipping:bill_list',
    }
    
    return render(request, 'shipping/billing/bill_form.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/')
def update_bill_status(request, bill_id):
    if request.method == 'POST':
        try:
            bill = get_object_or_404(Bill, id=bill_id)
            new_status = request.POST.get('status')
            
            # Validate status
            valid_statuses = dict(Bill.BILL_STATUS_CHOICES).keys()
            if new_status not in valid_statuses:
                messages.error(request, f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
                return redirect('shipping:bill_detail', bill_id=bill.id)
            
            old_status = bill.status
            
            # Don't process if status hasn't changed
            if old_status == new_status:
                messages.info(request, f'Bill #{bill.id} is already marked as {dict(Bill.BILL_STATUS_CHOICES).get(new_status)}')
                return redirect('shipping:bill_detail', bill_id=bill.id)
            
            # Update bill status
            bill.status = new_status
            bill.updated_at = timezone.now()
            
            # If marking as paid, set paid_at timestamp
            if new_status == 'PAID':
                bill.paid_at = timezone.now()
            
            bill.save()
            
            # Log the status change
            ActivityHistory.objects.create(
                user=request.user,
                activity_type='STATUS_CHANGED',
                description=f'Changed bill #{bill.id} status from {old_status} to {new_status}',
                reference_id=bill.id,
                reference_model='Bill',
                metadata={
                    'old_status': old_status,
                    'new_status': new_status,
                    'changed_by': request.user.id
                }
            )
            
            # Additional logging for specific status changes
            if new_status == 'PAID':
                ActivityHistory.objects.create(
                    user=request.user,
                    activity_type='BILL_PAID',
                    description=f'Marked bill #{bill.id} as paid',
                    reference_id=bill.id,
                    reference_model='Bill',
                    metadata={
                        'paid_amount': str(bill.amount),
                        'paid_by': request.user.id,
                        'paid_at': bill.paid_at.isoformat()
                    }
                )
            
            messages.success(
                request, 
                f'Bill #{bill.id} status updated from {dict(Bill.BILL_STATUS_CHOICES).get(old_status, old_status)} to {dict(Bill.BILL_STATUS_CHOICES).get(new_status, new_status)}.'
            )
            
            # Redirect to the appropriate page
            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
                
            return redirect('shipping:bill_detail', bill_id=bill.id)
            
        except Exception as e:
            messages.error(request, f'Error updating bill status: {str(e)}')
            if 'bill' in locals():
                return redirect('shipping:bill_detail', bill_id=bill.id)
    
    return redirect('shipping:bill_list')

@login_required
def bill_detail(request, bill_id):
    """View for displaying detailed information about a specific bill."""
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Get all activities related to this bill, ordered by most recent first
    activities = ActivityHistory.objects.filter(
        reference_model='Bill',
        reference_id=bill_id
    ).select_related('user').order_by('-created_at')
    
    # Calculate days until/since due date if it exists
    due_date_info = None
    if bill.due_date:
        today = timezone.now().date()
        delta = (bill.due_date - today).days
        
        if delta > 0:
            due_date_info = {
                'status': 'upcoming',
                'text': f'Due in {delta} day{"s" if delta > 1 else ""}',
                'class': 'text-blue-600'
            }
        elif delta < 0:
            due_date_info = {
                'status': 'overdue',
                'text': f'Overdue by {abs(delta)} day{"s" if abs(delta) > 1 else ""}',
                'class': 'text-red-600 font-medium'
            }
        else:
            due_date_info = {
                'status': 'today',
                'text': 'Due today',
                'class': 'text-yellow-600 font-medium'
            }
    
    # Get related bills for the same customer
    related_bills = Bill.objects.filter(
        customer=bill.customer
    ).exclude(id=bill.id).order_by('-created_at')[:5]
    
    # Calculate customer statistics
    customer_stats = {
        'total_bills': Bill.objects.filter(customer=bill.customer).count(),
        'total_paid': Bill.objects.filter(
            customer=bill.customer,
            status='PAID'
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
        'pending_bills': Bill.objects.filter(
            customer=bill.customer,
            status='PENDING'
        ).count(),
        'overdue_bills': Bill.objects.filter(
            customer=bill.customer,
            status='OVERDUE'
        ).count()
    }
    
    # Prepare context
    context = {
        'bill': bill,
        'activities': activities,
        'related_bills': related_bills,
        'customer_stats': customer_stats,
        'due_date_info': due_date_info,
        'status_choices': dict(Bill.BILL_STATUS_CHOICES),
        'can_edit': request.user.is_staff,
        'can_delete': request.user.is_superuser,
        'now': timezone.now()
    }
    
    return render(request, 'shipping/billing/bill_detail.html', context)

@login_required
def bill_list(request):
    """
    View for listing bills with filtering, sorting, and pagination.
    """
    # Initialize filter form with GET parameters
    filter_form = BillFilterForm(request.GET or None)
    
    # Start with base queryset
    bills = Bill.objects.select_related('customer').all()
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        bills = filter_form.get_filtered_queryset(bills)
    
    # Get pagination parameters from form or use defaults
    per_page = int(filter_form.data.get('per_page', 20))
    
    # Calculate summary statistics
    summary = bills.aggregate(
        total_bills=Count('id'),
        total_amount=Sum('amount'),
        avg_amount=Avg('amount'),
        pending_amount=Sum(
            Case(
                When(status='PENDING', then='amount'),
                default=Value(0),
                output_field=models.DecimalField()
            )
        ),
        paid_amount=Sum(
            Case(
                When(status='PAID', then='amount'),
                default=Value(0),
                output_field=models.DecimalField()
            )
        ),
        overdue_amount=Sum(
            Case(
                When(status='OVERDUE', then='amount'),
                default=Value(0),
                output_field=models.DecimalField()
            )
        )
    )
    
    # Get status counts
    status_counts = dict(Bill.BILL_STATUS_CHOICES)
    for status in status_counts:
        status_counts[status] = bills.filter(status=status).count()
    
    # Pagination
    paginator = Paginator(bills, per_page)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Check if it's an API request (from admin dashboard)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        # Return JSON response for API requests
        bill_list = []
        for bill in bills:
            bill_list.append({
                'id': bill.id,
                'customer': bill.customer.get_full_name() or bill.customer.username,
                'amount': float(bill.amount) if bill.amount is not None else 0.0,
                'status': bill.status,
                'created_at': bill.created_at.isoformat() if bill.created_at else None,
                'due_date': bill.due_date.isoformat() if bill.due_date else None,
                'payment_method': bill.payment_method,
                'description': bill.description,
            })
        return JsonResponse(bill_list, safe=False)
    
    # Prepare context for HTML response
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'status_counts': status_counts,
        'summary': summary,
        'total_bills': bills.count(),
        'can_create': request.user.is_staff,
        'now': timezone.now(),
    }
    
    return render(request, 'shipping/billing/bill_list.html', context)
