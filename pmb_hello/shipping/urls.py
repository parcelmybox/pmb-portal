from django.urls import path
from . import views
from . import views_billing

app_name = 'shipping'

urlpatterns = [
    path('tracking/', views.tracking, name='tracking'),
    path('addresses/', views.addresses, name='addresses'),
    path('rates/', views.rates, name='rates'),
    
    # Billing URLs
    path('bills/', views_billing.bill_list, name='bill_list'),
    path('bills/create/', views_billing.create_bill, name='create_bill'),
    path('bills/<int:bill_id>/', views_billing.bill_detail, name='bill_detail'),
    path('bills/<int:bill_id>/update-status/', views_billing.update_bill_status, name='update_bill_status'),
]
