from django.shortcuts import render
from .models import Category

def category_list(request):
    categories = Category.objects.all()
    return render(request, "category_list.html", {"categories": categories})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def shipping_price_form(request):
    # Render the HTML form page
    return render(request, 'category/shipping_price_form.html')

def shipping_price_api(request):
    # This handles the POST AJAX request and returns JSON price
    if request.method == 'POST':
        data = json.loads(request.body)
        source_pin = data.get('source_pin')
        destination_zip = data.get('destination_zip')
        weight = float(data.get('weight', 0))

        # Your price calculation logic, for example:
        estimated_price = weight * 2  # Simple formula

        return JsonResponse({'estimated_price': estimated_price})
    else:
        return JsonResponse({'error': 'Only POST requests allowed'}, status=400)
