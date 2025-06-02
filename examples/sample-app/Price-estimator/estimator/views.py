from .models import ShippingOrder
from django.shortcuts import redirect,render
def shipping_form(request):
    if request.method == 'POST':
        pickup_city = request.POST['pickup_city']
        destination_country = request.POST['destination_country']
        destination_zip = request.POST.get('destination_zip')  # ✅ safe, returns None if missing

        carrier = request.POST['carrier']
        package_type = request.POST['package_type']

        # Pricing logic
        rate_map = {'DHL': 3000, 'FedEx': 2500, 'UPS': 2400}
        ship_days_map = {'DHL': 3, 'FedEx': 5, 'UPS': 7}

        length = float(request.POST.get('length') or 0)
        width = float(request.POST.get('width') or 0)
        height = float(request.POST.get('height') or 0)

        volumetric_weight = None
        price = 0

        if package_type == 'Box':
            volumetric_weight = (length * width * height) / 5000  # DHL standard
            price = rate_map[carrier] * volumetric_weight
        else:
            volumetric_weight = None
            price = rate_map[carrier]  # Flat rate for documents


        # Save to DB
        order = ShippingOrder.objects.create(
            pickup_city=pickup_city,
            destination_country=destination_country,
            destination_zip=destination_zip,
            carrier=carrier,
            package_type=package_type,
            length=length if package_type == 'Box' else None,
            width=width if package_type == 'Box' else None,
            height=height if package_type == 'Box' else None,
            volumetric_weight=round(volumetric_weight, 2) if volumetric_weight else None,
             price=round(price, 2),
            ship_days=ship_days_map[carrier]
        )

        # Pass the order ID via session or query param
        return redirect('result_page', order_id=order.id)

    return render(request, 'estimator/form.html')
def result_page(request, order_id):
    order = ShippingOrder.objects.get(id=order_id)
    return render(request, 'estimator/result.html', {'order': order})

from django.http import JsonResponse
from .models import ShippingOrder

def orders_api(request):
    orders = ShippingOrder.objects.all().order_by('-created_at')

    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'pickup_city': order.pickup_city,
            'destination_country': order.destination_country,
            'destination_zip': order.destination_zip,
            'carrier': order.carrier,
            'package_type': order.package_type,
            'length': order.length,
            'width': order.width,
            'height': order.height,
            'volumetric_weight': order.volumetric_weight,
            'price': order.price,
            'ship_days': order.ship_days,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    return JsonResponse(data, safe=False)

