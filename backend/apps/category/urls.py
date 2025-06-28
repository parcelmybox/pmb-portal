# category/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('shipping-price/', views.shipping_price_form, name='shipping_price_form'),
    path('api/shipping-price/', views.shipping_price_api, name='shipping_price_api'),
]
