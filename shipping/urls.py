from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    path('', views.shipping_home, name='shipping_home'),
    path('create/', views.create_shipment, name='create_shipment'),
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('tracking/<str:tracking_number>/', views.tracking, name='tracking'),
    path('addresses/', views.manage_addresses, name='manage_addresses'),
    path('address/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),
]
