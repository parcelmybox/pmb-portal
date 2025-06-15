from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
from io import BytesIO

from .models import Invoice
from .activity import ActivityHistory
from .forms import InvoiceForm
from django.contrib.auth import get_user_model

User = get_user_model()

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'shipping/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            # Non-staff users only see their own invoices
            queryset = queryset.filter(customer=self.request.user)
        return queryset.order_by('-created_at')

def invoice_detail(request, invoice_id):
    """View for displaying invoice details."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check permissions
    if not request.user.is_staff and invoice.customer != request.user:
        return HttpResponseForbidden("You don't have permission to view this invoice.")
    
    context = {
        'invoice': invoice,
        'shipment': invoice.shipment,
        'can_edit': request.user.is_staff,
    }
    
    # Use the correct template path
    return render(request, 'shipping/invoices/detail.html', context)

def export_invoice_pdf(request, invoice_id):
    """Export invoice as PDF."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check permissions
    if not request.user.is_staff and invoice.customer != request.user:
        return HttpResponseForbidden("You don't have permission to export this invoice.")
    
    # Render the HTML template
    template = get_template('shipping/invoices/pdf.html')
    context = {
        'invoice': invoice,
        'shipment': invoice.shipment,
        'request': request,  # Add request to context for URL resolution in template
    }
    html = template.render(context)
    
    # Create PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
        return response
    
    return HttpResponse('Error generating PDF', status=500)

@login_required
@permission_required('shipping.change_invoice', raise_exception=True)
def update_invoice_status(request, invoice_id):
    """Update invoice status (e.g., mark as paid)."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Invoice.INVOICE_STATUS_CHOICES):
            old_status = invoice.status
            invoice.status = new_status
            
            # If marking as paid, set payment date
            if new_status == 'paid' and old_status != 'paid':
                invoice.payment_date = timezone.now()
            
            invoice.save()
            
            # Log the status change
            ActivityHistory.log_activity(
                user=request.user,
                action=f'Invoice status changed from {old_status} to {new_status}',
                obj=invoice,
                request=request
            )
            
            messages.success(request, 'Invoice status updated successfully.')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('shipping:invoice_detail', invoice_id=invoice.id)

@login_required
@permission_required('shipping.change_invoice', raise_exception=True)
def edit_invoice(request, invoice_id):
    """Edit invoice details."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            
            # Log the edit
            ActivityHistory.log_activity(
                user=request.user,
                action='Invoice details updated',
                obj=invoice,
                request=request
            )
            
            messages.success(request, 'Invoice updated successfully.')
            return redirect('shipping:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm(instance=invoice)
    
    return render(request, 'shipping/invoice_edit.html', {
        'form': form,
        'invoice': invoice,
    })

@login_required
@permission_required('shipping.delete_invoice', raise_exception=True)
@require_http_methods(["POST"])
@login_required
@permission_required('shipping.add_invoice', raise_exception=True)
def create_invoice(request):
    """Create a new invoice."""
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            if not invoice.created_by_id:
                invoice.created_by = request.user
            invoice.save()
            form.save_m2m()  # Save many-to-many relationships if any
            
            # Log the creation
            ActivityHistory.log_activity(
                user=request.user,
                action='Invoice created',
                obj=invoice,
                request=request
            )
            
            messages.success(request, 'Invoice created successfully.')
            return redirect('shipping:invoice_detail', invoice_id=invoice.id)
    else:
        # Set default values for new invoice
        initial = {
            'status': 'draft',
            'due_date': timezone.now().date() + timezone.timedelta(days=30),
            'created_by': request.user.id,
        }
        # If customer_id is provided in GET params, pre-select that customer
        customer_id = request.GET.get('customer_id')
        if customer_id and request.user.is_staff:
            try:
                customer = User.objects.get(id=customer_id)
                initial['customer'] = customer
            except User.DoesNotExist:
                pass
                
        form = InvoiceForm(initial=initial)
        
        # Non-staff users can only create invoices for themselves
        if not request.user.is_staff:
            form.fields['customer'].queryset = User.objects.filter(id=request.user.id)
            form.initial['customer'] = request.user
    
    return render(request, 'shipping/invoice_edit.html', {
        'form': form,
        'is_new': True,
    })


def delete_invoice(request, invoice_id):
    """Delete an invoice."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    shipment_id = invoice.shipment.id if invoice.shipment else None
    
    # Log the deletion before actually deleting
    ActivityHistory.log_activity(
        user=request.user,
        action='Invoice deleted',
        obj=invoice,
        request=request
    )
    
    invoice.delete()
    messages.success(request, 'Invoice has been deleted.')
    
    if shipment_id:
        return redirect('shipping:shipment_detail', pk=shipment_id)
    return redirect('shipping:invoice_list')
