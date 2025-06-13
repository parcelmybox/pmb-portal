from django.urls import path, include
from . import views
from .views_billing import (
    create_bill, 
    bill_detail, 
    BillListView, 
    update_bill_status,
    export_bill_pdf,
    delete_bill,
    edit_bill
)
from .views import PricingView

app_name = 'shipping'

urlpatterns = [
    path('', views.shipping_home, name='shipping_home'),
    path('create/', views.create_shipment, name='create_shipment'),
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('tracking/<str:tracking_number>/', views.tracking, name='tracking'),
    path('addresses/', views.manage_addresses, name='manage_addresses'),
    path('address/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('track/', views.tracking_input_page, name='tracking_input_page'), # Page for entering tracking number
    
    # New pricing page
    path('pricing/', PricingView.as_view(), name='pricing'),
    
    # Billing URLs
    path('bills/', BillListView.as_view(), name='bill_list'),
    path('bills/create/', create_bill, name='create_bill'),
    path('bills/<int:bill_id>/', bill_detail, name='bill_detail'),
    path('bills/<int:bill_id>/export/', export_bill_pdf, name='export_bill_pdf'),
    path('bills/<int:bill_id>/update-status/', update_bill_status, name='update_bill_status'),
    path('bills/<int:bill_id>/edit/', edit_bill, name='edit_bill'),
    path('bills/<int:bill_id>/delete/', delete_bill, name='delete_bill'),
]
