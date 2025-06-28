from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Address, Shipment, ShippingRate
from .forms import AddressForm, ShipmentForm

def tracking(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
            return render(request, 'shipping/tracking_detail.html', {'shipment': shipment})
        except Shipment.DoesNotExist:
            messages.error(request, 'Shipment not found')
    return render(request, 'shipping/tracking.html')

def addresses(request):
    addresses = Address.objects.all()
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address added successfully')
            return redirect('shipping:addresses')
    else:
        form = AddressForm()
    return render(request, 'shipping/addresses.html', {
        'addresses': addresses,
        'form': form
    })

def rates(request):
    rates = ShippingRate.objects.all()
    return render(request, 'shipping/rates.html', {'rates': rates})
