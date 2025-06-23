import logging
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
from django.utils import timezone
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from .models import Shipment, ShippingAddress, ShipmentItem, TrackingEvent, Invoice
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from .activity import ActivityHistory
from .forms import ShipmentForm, ShippingAddressForm

@require_http_methods(["POST"])
@login_required
def set_default_address(request, pk):
    """Set an address as the default shipping address"""
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    
    with transaction.atomic():
        # Set all addresses to not default
        ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        # Set the selected address as default
        address.is_default = True
        address.save()
    
    messages.success(request, 'Default shipping address updated successfully.')
    return redirect('shipping:manage_addresses')

class PricingView(TemplateView):
    template_name = 'shipping/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any pricing data to the context
        context['pricing_tiers'] = [
            {
                'name': 'Standard',
                'price': 'From $5.99',
                'features': ['Up to 2kg', '3-5 business days', 'Tracking included'],
                'popular': False
            },
            {
                'name': 'Express',
                'price': 'From $9.99',
                'features': ['Up to 5kg', '1-2 business days', 'Priority support'],
                'popular': True
            },
            {
                'name': 'Premium',
                'price': 'From $14.99',
                'features': ['Up to 10kg', 'Next day delivery', '24/7 support'],
                'popular': False
            }
        ]
        return context

@login_required
def shipping_home(request):
    """Display the shipping home page with the user's shipments."""
    # Get the user's shipments, ordered by most recent first
    shipments = Shipment.objects.filter(
        sender_address__user=request.user
    ).select_related('sender_address', 'recipient_address').order_by('-created_at')
    
    context = {
        'shipments': shipments,
        'title': 'My Shipments',
    }
    return render(request, 'shipping/home.html', context)

def calculate_shipping_cost(package_type, weight):
    """
    Calculate shipping cost based on package type and weight.
    This is a simplified calculation - adjust the rates as needed.
    """
    # Base rates by package type (in USD)
    base_rates = {
        'document': 5.00,
        'parcel': 10.00,
        'oversized': 25.00,
        'liquid': 15.00,
        'fragile': 20.00,
    }
    
    # Rate per kg
    rate_per_kg = 2.00
    
    # Get base rate for package type, default to parcel if not found
    base_rate = base_rates.get(package_type, 10.00)
    
    # Calculate total cost
    total_cost = base_rate + (float(weight) * rate_per_kg)
    
    # Round to 2 decimal places
    return round(total_cost, 2)

def create_shipment(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Save the shipment first
                    shipment = form.save(commit=False)
                    
                    # Calculate shipping cost
                    shipping_cost = calculate_shipping_cost(
                        shipment.package_type,
                        shipment.weight
                    )
                    shipment.shipping_cost = shipping_cost
                    
                    # Set the tracking number if not set
                    if not shipment.tracking_number:
                        shipment.tracking_number = generate_tracking_number()
                    shipment.save()
                    
                    # Save the many-to-many relationships
                    form.save_m2m()
                    
                    # Process shipment items
                    item_names = request.POST.getlist('item_name')
                    item_quantities = request.POST.getlist('item_quantity')
                    item_descriptions = request.POST.getlist('item_description')
                    
                    # Create shipment items
                    for name, quantity, description in zip(item_names, item_quantities, item_descriptions):
                        if name and quantity:  # Only create if name and quantity are provided
                            ShipmentItem.objects.create(
                                shipment=shipment,
                                name=name,
                                quantity=quantity,
                                description=description
                            )
                    
                    # Create initial tracking event
                    TrackingEvent.objects.create(
                        shipment=shipment,
                        status='pending',
                        location='Processing Center',
                        description='Shipment created and awaiting processing'
                    )
                    
                    # Generate invoice for the shipment
                    try:
                        # Ensure we have all required fields for invoice generation
                        if not shipment.sender_address or not shipment.sender_address.user:
                            raise ValueError('No sender address or user associated with the shipment')
                            
                        if not shipment.shipping_cost:
                            raise ValueError('Shipping cost is not set')
                            
                        # Generate the invoice
                        invoice = shipment.generate_invoice(created_by=request.user, request=request)
                        
                        # Refresh the shipment to ensure we have the latest data
                        shipment.refresh_from_db()
                        
                        # Verify the invoice was created and linked
                        if hasattr(shipment, 'invoice') and shipment.invoice:
                            messages.success(request, f'Shipment created successfully! Invoice #{invoice.id} has been generated.')
                        else:
                            raise ValueError('Invoice was not properly linked to the shipment')
                            
                    except Exception as e:
                        # Log the error but don't fail the shipment creation
                        logger = logging.getLogger(__name__)
                        logger.error(f'Error generating invoice for shipment {shipment.id}: {str(e)}', exc_info=True)
                        messages.warning(
                            request,
                            'Shipment created, but there was an error generating the invoice. '\
                            'Please generate it manually from the shipment details.'
                        )
                    
                    # Log the shipment creation activity
                    try:
                        from .activity import ActivityHistory
                        ActivityHistory.log_activity(
                            user=request.user,
                            action='Created shipment',
                            obj=shipment,
                            request=request
                        )
                    except Exception as e:
                        logger.error(f'Error logging shipment creation activity: {str(e)}', exc_info=True)
                    
                    return redirect('shipping:shipment_detail', pk=shipment.pk)
                    
            except Exception as e:
                error_msg = f'Error creating shipment: {str(e)}'
                messages.error(request, error_msg)
                # Log the error for debugging
                logger = logging.getLogger(__name__)
                logger.error(error_msg, exc_info=True)
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ShipmentForm(user=request.user)
        
    # Get user's addresses for the form
    user_addresses = ShippingAddress.objects.filter(user=request.user)
    
    return render(request, 'shipping/create_shipment.html', {
        'form': form,
        'user_addresses': user_addresses
    })

@login_required
def shipment_detail(request, pk):
    """View for displaying shipment details and related invoice."""
    shipment = get_object_or_404(
        Shipment.objects.select_related('sender_address', 'recipient_address'), 
        pk=pk
    )
    
    # Check if the user has permission to view this shipment
    if not request.user.is_staff and shipment.sender_address.user != request.user:
        messages.error(request, 'You do not have permission to view this shipment.')
        return redirect('shipping:shipping_home')
    
    # Get the related invoice if it exists
    invoice = None
    if hasattr(shipment, 'invoice'):
        invoice = shipment.invoice
    
    # Check if the current user can generate an invoice
    can_generate_invoice = (
        not invoice and  # No invoice exists yet
        (request.user.is_staff or shipment.sender_address.user == request.user) and  # User has permission
        shipment.status not in ['cancelled']  # Shipment is not cancelled
    )
    
    # Debug information
    print("\n=== DEBUG: Shipment Detail View ===")
    print(f"Shipment ID: {shipment.id}")
    print(f"Sender Address ID: {shipment.sender_address_id}")
    print(f"Recipient Address ID: {shipment.recipient_address_id}")
    print(f"Sender Name: {shipment.sender_address.first_name} {shipment.sender_address.last_name}")
    print(f"Recipient Name: {shipment.recipient_address.first_name} {shipment.recipient_address.last_name}")
    print("=== END DEBUG ===\n")
    
    context = {
        'shipment': shipment,
        'invoice': invoice,
        'can_generate_invoice': can_generate_invoice,
        'can_edit': request.user.is_staff or shipment.sender_address.user == request.user,
    }
    
    return render(request, 'shipping/shipment_detail.html', context)

@require_GET
@login_required
def get_address_details(request, pk):
    """API endpoint to get address details by ID"""
    try:
        address = ShippingAddress.objects.get(pk=pk, user=request.user)
        return JsonResponse({
            'id': address.id,
            'first_name': address.first_name,
            'last_name': address.last_name,
            'address_line1': address.address_line1,
            'address_line2': address.address_line2 or '',
            'city': address.city,
            'state': address.state,
            'country': address.country,
            'postal_code': address.postal_code,
            'phone_number': address.phone_number
        })
    except ShippingAddress.DoesNotExist:
        return JsonResponse({'error': 'Address not found'}, status=404)

@require_http_methods(["POST"])
@login_required
def add_address_ajax(request):
    """AJAX endpoint to add a new address from the shipment form"""
    try:
        # Create a form instance with the submitted data
        form = ShippingAddressForm(data=request.POST, user=request.user)
        
        if form.is_valid():
            # Save the new address
            address = form.save(commit=False)
            address.user = request.user
            
            # Set as default if this is the first address or explicitly set
            is_default = request.POST.get('is_default') == 'on' or not ShippingAddress.objects.filter(user=request.user).exists()
            if is_default:
                # Unset any existing default address
                ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
                address.is_default = True
            
            address.save()
            
            # Return success response with address details
            return JsonResponse({
                'success': True,
                'address_id': address.id,
                'address_text': f"{address.first_name} {address.last_name}, {address.city}, {address.country}",
                'first_name': address.first_name,
                'last_name': address.last_name
            })
        else:
            # Return form validation errors
            return JsonResponse({
                'success': False,
                'error': 'Validation error',
                'errors': dict(form.errors.items())
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def tracking_input_page(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number', '')
        if tracking_number:
            return redirect(reverse('shipping:tracking', kwargs={'tracking_number': tracking_number}))
        else:
            messages.error(request, 'Please enter a tracking number.')
            return render(request, 'shipping/tracking_input_page.html')
    return render(request, 'shipping/tracking_input_page.html')

def tracking(request, tracking_number):
    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
        tracking_events = shipment.tracking_events.all().order_by('timestamp')
        return render(request, 'shipping/tracking.html', {
            'shipment': shipment,
            'tracking_events': tracking_events
        })
    except Shipment.DoesNotExist:
        messages.error(request, 'Shipment not found')
        return redirect('shipping:shipping_home')

def manage_addresses(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Address saved successfully!')
                return redirect('shipping:manage_addresses')
            except Exception as e:
                messages.error(request, f'Error saving address: {str(e)}')
        else:
            # Show form errors to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ShippingAddressForm(user=request.user)
    
    # Only show addresses for the current user
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    return render(request, 'shipping/manage_addresses.html', {
        'addresses': addresses,
        'form': form
    })

@login_required
def add_address(request):
    """
    Add a new shipping address.
    """
    next_url = request.GET.get('next', 'shipping:manage_addresses')
    address_type = request.GET.get('address_type', '').lower()
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                address = form.save(commit=False)
                address.user = request.user
                
                # If this is the first address, set it as default
                if not ShippingAddress.objects.filter(user=request.user).exists():
                    address.is_default = True
                
                address.save()
                messages.success(request, 'Address added successfully!')
                
                # If coming from shipment creation, return to that page
                if 'create' in next_url:
                    return redirect('shipping:create_shipment')
                return redirect(next_url)
                
            except Exception as e:
                messages.error(request, f'Error saving address: {str(e)}')
        else:
            # Show form errors to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ShippingAddressForm(user=request.user)
    
    # Set the page title based on address type
    title = 'Add New Address'
    if address_type == 'sender':
        title = 'Add Sender Address'
    elif address_type == 'recipient':
        title = 'Add Recipient Address'
    
    return render(request, 'shipping/add_address.html', {
        'form': form,
        'title': title,
        'next_url': next_url,
        'address_type': address_type
    })

def edit_address(request, pk):
    """Edit an existing shipping address."""
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Address updated successfully.')
                return redirect('shipping:manage_addresses')
            except Exception as e:
                messages.error(request, f'Error updating address: {str(e)}')
        else:
            # Show form errors to the user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ShippingAddressForm(instance=address, user=request.user)
    
    return render(request, 'shipping/edit_address.html', {
        'form': form,
        'address': address
    })

def delete_address(request, pk):
    """Delete a shipping address."""
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    
    if request.method == 'POST':
        try:
            address.delete()
            messages.success(request, 'Address deleted successfully.')
            return redirect('shipping:manage_addresses')
        except Exception as e:
            messages.error(request, f'Error deleting address: {str(e)}')
            return redirect('shipping:manage_addresses')
    
    return render(request, 'shipping/delete_address_confirm.html', {'address': address})

def generate_tracking_number():
    # Generate a tracking number in the format: PMB-YYYYMMDD-XXXXX
    from datetime import datetime
    import random
    import string
    
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"PMB-{date_str}-{random_str}"

@login_required
def generate_shipment_invoice(request, pk):
    """Generate an invoice for a shipment."""
    shipment = get_object_or_404(Shipment, pk=pk)
    
    # Check permissions - only staff or the shipment owner can generate an invoice
    if not request.user.is_staff and shipment.sender_address.user != request.user:
        messages.error(request, 'You do not have permission to generate an invoice for this shipment.')
        return redirect('shipping:shipment_detail', pk=shipment.pk)
    
    try:
        # Generate the invoice
        invoice = shipment.generate_invoice(created_by=request.user, request=request)
        
        # Log the activity
        ActivityHistory.log_activity(
            user=request.user,
            action='Invoice Generated',
            obj=invoice,
            request=request
        )
        
        messages.success(request, f'Invoice #{invoice.id} has been generated successfully.')
        return redirect('shipping:shipment_detail', pk=shipment.pk)
    except Exception as e:
        messages.error(request, f'Error generating invoice: {str(e)}')
        return redirect('shipping:shipment_detail', pk=shipment.pk)

@login_required
def generate_shipment_bill(request, pk):
    """Legacy endpoint for generating a bill (now generates an invoice)."""
    return generate_shipment_invoice(request, pk)

@login_required
@require_http_methods(["POST"])
def cancel_shipment(request, pk):
    """Cancel a shipment."""
    from .activity import ActivityHistory
    
    shipment = get_object_or_404(Shipment, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and shipment.sender_address.user != request.user:
        return HttpResponseForbidden("You don't have permission to cancel this shipment.")
    
    # Check if shipment can be cancelled
    if shipment.status in ['cancelled', 'delivered']:
        messages.error(request, f"Cannot cancel a shipment that is already {shipment.get_status_display().lower()}.")
        return redirect('shipping:shipment_detail', pk=shipment.pk)
    
    try:
        # Update shipment status
        old_status = shipment.status
        shipment.status = 'cancelled'
        shipment.save()
        
        # Create tracking event
        TrackingEvent.objects.create(
            shipment=shipment,
            status='cancelled',
            location=f"{shipment.sender_address.city}, {shipment.sender_address.state}",
            description=f"Shipment cancelled by {request.user.get_full_name() or request.user.username}"
        )
        
        # Log activity using the helper method
        ActivityHistory.log_activity(
            user=request.user,
            action='Shipment Cancelled',
            obj=shipment,
            request=request
        )
        
        messages.success(request, f"Shipment #{shipment.tracking_number} has been cancelled successfully.")
        
    except Exception as e:
        messages.error(request, f"Error cancelling shipment: {str(e)}")
    
    return redirect('shipping:shipment_detail', pk=shipment.pk)


def print_shipping_label(request, pk):
    """Generate a PDF shipping label for a shipment."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from io import BytesIO
    import qrcode
    
    shipment = get_object_or_404(Shipment, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and shipment.sender_address.user != request.user:
        return HttpResponseForbidden("You don't have permission to view this label.")
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Draw the shipping label
    p.setFont("Helvetica-Bold", 14)
    p.drawString(72, height - 72, "SHIPPING LABEL")
    p.line(72, height - 80, width - 72, height - 80)
    
    # Add shipping information
    p.setFont("Helvetica", 10)
    y = height - 100
    
    # From address
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, y, "FROM:")
    p.setFont("Helvetica", 10)
    y -= 20
    # Get the user's full name for the sender
    sender_name = shipment.sender_address.user.get_full_name() if shipment.sender_address.user else "Sender"
    p.drawString(72, y, sender_name)
    y -= 15
    p.drawString(72, y, shipment.sender_address.address_line1)
    if shipment.sender_address.address_line2:
        y -= 15
        p.drawString(72, y, shipment.sender_address.address_line2)
    y -= 15
    p.drawString(72, y, f"{shipment.sender_address.city}, {shipment.sender_address.state} {shipment.sender_address.postal_code}")
    y -= 15
    p.drawString(72, y, str(shipment.sender_address.country))
    
    # Add phone number if available
    if shipment.sender_address.phone_number:
        y -= 15
        p.drawString(72, y, f"Phone: {shipment.sender_address.phone_number}")
    
    # To address
    y -= 40  # Extra space before TO section
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, y, "TO:")
    p.setFont("Helvetica", 10)
    y -= 20
    # For recipient, we'll use the address as is since we don't have a contact name
    p.drawString(72, y, "Recipient")
    y -= 15
    p.drawString(72, y, shipment.recipient_address.address_line1)
    if shipment.recipient_address.address_line2:
        y -= 15
        p.drawString(72, y, shipment.recipient_address.address_line2)
    y -= 15
    p.drawString(72, y, f"{shipment.recipient_address.city}, {shipment.recipient_address.state} {shipment.recipient_address.postal_code}")
    y -= 15
    p.drawString(72, y, str(shipment.recipient_address.country))
    
    # Add phone number if available
    if shipment.recipient_address.phone_number:
        y -= 15
        p.drawString(72, y, f"Phone: {shipment.recipient_address.phone_number}")
    
    # Package info
    y -= 40
    p.setFont("Helvetica-Bold", 12)
    p.drawString(72, y, "SHIPMENT DETAILS:")
    p.setFont("Helvetica", 10)
    y -= 20
    p.drawString(72, y, f"Tracking #: {shipment.tracking_number}")
    y -= 15
    p.drawString(72, y, f"Package Type: {shipment.get_package_type_display()}")
    y -= 15
    p.drawString(72, y, f"Weight: {shipment.weight} kg")
    y -= 15
    p.drawString(72, y, f"Status: {shipment.get_status_display()}")
    
    # Add a QR code with tracking info if qrcode is available
    try:
        import qrcode
        try:
            qr = qrcode.QRCode(version=1, box_size=4, border=4)
            qr.add_data(f"Tracking Number: {shipment.tracking_number}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to a BytesIO object
            img_io = BytesIO()
            qr_img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Draw QR code on PDF
            qr_img_reader = ImageReader(img_io)
            p.drawImage(qr_img_reader, width - 200, height - 200, width=100, height=100)
        except Exception as e:
            # If QR code generation fails, just add the tracking number as text
            p.setFont("Helvetica", 8)
            p.drawString(width - 200, height - 220, f"Tracking: {shipment.tracking_number}")
    except ImportError:
        # If qrcode package is not available, just add the tracking number as text
        p.setFont("Helvetica", 8)
        p.drawString(width - 200, height - 220, f"Tracking: {shipment.tracking_number}")
    
    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    
    # File response for the PDF
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="shipping_label_{shipment.tracking_number}.pdf"'
    return response
