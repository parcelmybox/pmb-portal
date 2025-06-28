from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'customers'

urlpatterns = [
    # Authentication URLs
    path('signup/', views.SignUpView.as_view(), name='account_signup'),
    
    # Add customer-related URL patterns here
    # Example:
    # path('', views.CustomerListView.as_view(), name='customer_list'),
]
