from django.urls import path, include
from . import views
from .views_test import test_auth, test_login_required
from .views_debug import debug_user, protected_debug, debug_billing_stats
from .views_billing import (
    create_bill, 
    bill_detail, 
    BillListView, 
    update_bill_status,
    export_bill_pdf,
    delete_bill,
    edit_bill
)
from .views_invoice import (
    invoice_detail,
    InvoiceListView,
    export_invoice_pdf,
    update_invoice_status,
    delete_invoice,
    edit_invoice,
    create_invoice
)
from .test_pdf_view import test_pdf_view
from .views_customer import CustomerSearchView
from .views import PricingView
from .views import get_courier_plans

app_name = 'shipping'

urlpatterns = [
    path('', views.shipping_home, name='shipping_home'),
    path('create/', views.create_shipment, name='create_shipment'),
    path('shipment/<int:pk>/', views.shipment_detail, name='shipment_detail'),
    path('shipment/<int:pk>/cancel/', views.cancel_shipment, name='cancel_shipment'),
    path('shipment/<int:pk>/print-label/', views.print_shipping_label, name='print_shipping_label'),
    path('shipment/<int:pk>/generate-bill/', views.generate_shipment_bill, name='generate_shipment_bill'),
    path('shipment/<int:pk>/generate-invoice/', views.generate_shipment_invoice, name='generate_shipment_invoice'),
    path('tracking/<str:tracking_number>/', views.tracking, name='tracking'),
    path('addresses/', views.manage_addresses, name='manage_addresses'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('address/set-default/<int:pk>/', views.set_default_address, name='set_default_address'),
    path('track/', views.tracking_input_page, name='tracking_input_page'), # Page for entering tracking number
    
    # New pricing page
    path('pricing/', PricingView.as_view(), name='pricing'),
    
    # API Endpoints
    path('api/addresses/<int:pk>/', views.get_address_details, name='api_address_details'),
    path('api/addresses/add/', views.add_address_ajax, name='add_address_ajax'),
    
    # Billing URLs (legacy)
    path('bills/', BillListView.as_view(), name='bill_list'),
    path('bills/create/', create_bill, name='create_bill'),
    path('bills/<int:bill_id>/', bill_detail, name='bill_detail'),
    path('bills/<int:bill_id>/export/', export_bill_pdf, name='export_bill_pdf'),
    path('bills/<int:bill_id>/update-status/', update_bill_status, name='update_bill_status'),
    path('bills/<int:bill_id>/edit/', edit_bill, name='edit_bill'),
    path('bills/<int:bill_id>/delete/', delete_bill, name='delete_bill'),
    
    # Invoice URLs
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', create_invoice, name='create_invoice'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/export/', export_invoice_pdf, name='export_invoice_pdf'),
    path('invoices/<int:invoice_id>/update-status/', update_invoice_status, name='update_invoice_status'),
    path('invoices/<int:invoice_id>/edit/', edit_invoice, name='edit_invoice'),
    path('invoices/<int:invoice_id>/delete/', delete_invoice, name='delete_invoice'),
    path('customers/search/', CustomerSearchView.as_view(), name='customer_search'),
    
    # Test and Debug URLs
    path('test-pdf/', test_pdf_view, name='test_pdf'),
    path('test-auth/', test_auth, name='test_auth'),
    path('test-login-required/', test_login_required, name='test_login_required'),
    path('debug/user/', debug_user, name='debug_user'),
    path('debug/protected/', protected_debug, name='debug_protected'),
    path('debug/billing/', debug_billing_stats, name='debug_billing'),
    
    
    path('courier-plans/', get_courier_plans, name='get_courier_plans'),
    #path('', include('shipping.urls')),
]
