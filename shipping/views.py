from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.utils import timezone
from django.views.generic import TemplateView
from .models import Shipment, ShippingAddress, ShipmentItem, TrackingEvent
from .forms import ShipmentForm, ShippingAddressForm

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

def shipping_home(request):
    shipments = Shipment.objects.select_related('sender_address', 'recipient_address').order_by('-created_at')
    return render(request, 'shipping/shipment_list.html', {'shipments': shipments})

def create_shipment(request):
    if request.method == 'POST':
        form = ShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.tracking_number = generate_tracking_number()
            shipment.save()
            
            # Create tracking event
            TrackingEvent.objects.create(
                shipment=shipment,
                status='pending',
                location='Processing Center',
                description='Shipment created and awaiting processing'
            )
            
            messages.success(request, 'Shipment created successfully!')
            return redirect('shipping:shipment_detail', pk=shipment.pk)
    else:
        form = ShipmentForm()
    return render(request, 'shipping/create_shipment.html', {'form': form})

def shipment_detail(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    return render(request, 'shipping/shipment_detail.html', {'shipment': shipment})

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

def edit_address(request, pk):
    address = get_object_or_404(ShippingAddress, pk=pk, contact__user=request.user)
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('shipping:manage_addresses')
    else:
        form = ShippingAddressForm(instance=address)
    return render(request, 'shipping/edit_address.html', {'form': form, 'address': address})

def delete_address(request, pk):
    address = get_object_or_404(ShippingAddress, pk=pk, contact__user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('shipping:manage_addresses')
    return render(request, 'shipping/delete_address.html', {'address': address})

def manage_addresses(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save()
            messages.success(request, 'Address saved successfully!')
            return redirect('shipping:manage_addresses')
    else:
        form = ShippingAddressForm()
    
    addresses = ShippingAddress.objects.all()
    return render(request, 'shipping/manage_addresses.html', {
        'addresses': addresses,
        'form': form
    })

def generate_tracking_number():
    """Generate a unique tracking number"""
    import random
    import string
    prefix = 'PMB'
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"{prefix}{random_chars}"

def edit_address(request, pk):
    """Edit an existing shipping address."""
    address = get_object_or_404(ShippingAddress, pk=pk)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('shipping:manage_addresses')
    else:
        form = ShippingAddressForm(instance=address)
    
    return render(request, 'shipping/edit_address.html', {
        'form': form,
        'address': address
    })

def delete_address(request, pk):
    """Delete a shipping address."""
    address = get_object_or_404(ShippingAddress, pk=pk)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect('shipping:manage_addresses')
    return render(request, 'shipping/delete_address_confirm.html', {'address': address})
