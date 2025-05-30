from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Shipment, ShippingAddress, ShipmentItem, TrackingEvent
from .forms import ShipmentForm, ShippingAddressForm

def shipping_home(request):
    recent_shipments = Shipment.objects.order_by('-created_at')[:5]
    return render(request, 'shipping/home.html', {
        'recent_shipments': recent_shipments
    })

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
    prefix = 'PMB-'
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return prefix + random_part
