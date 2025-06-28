"""
URL configuration for pmb_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
# Import views from the apps
from apps.category import views as category_views
from . import views as pmb_core_views
from .admin import custom_admin_site  # Import our custom admin site

# Import the default admin site's logout view
from django.contrib.auth.views import LogoutView
from django.views.decorators.http import require_http_methods

# Admin-specific logout view that handles both GET and POST
@require_http_methods(["GET", "POST"])
def admin_logout(request):
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    from django.contrib import messages
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return HttpResponseRedirect(reverse('admin:login'))

# API URLs - Include first to avoid conflicts with other URL patterns
api_patterns = [
    path('', include('api.urls')),  # Our new API endpoints
]

urlpatterns = [
    # API endpoints
    path('api/', include(api_patterns)),
    
    # API Documentation
    path('api/docs/', RedirectView.as_view(url='/api/swagger/', permanent=False), name='api-docs'),
    
    # Main site
    path('', pmb_core_views.site_home_page, name='site_home_page'),  # Site home page
    path('admin/logout/', admin_logout, name='admin-logout'),  # Admin logout - Fixed the URL name to avoid ':'
    path('admin/', custom_admin_site.urls),  # Use our custom admin site
    
    # Customers app URLs
    path('customers/', include('customers.urls')),
    
    # Shipping app URLs
    path('shipping/', include('shipping.urls')),
    
    # Redirect old pricing URL to new one
    path('shipping/pricing/', RedirectView.as_view(url='/shipping-price/', permanent=True)),
    # Redirect old billing URLs to new ones
    path('admin/shipping/bill/', RedirectView.as_view(url='/shipping/bills/', permanent=True)),
    path('admin/shipping/bill/add/', RedirectView.as_view(url='/shipping/bills/create/', permanent=True)),
    path('shipping/', include('shipping.urls')),
    path('categories/', category_views.category_list, name='category_list'),
    path('shipping-price/', category_views.shipping_price_form, name='shipping_price_form'),
    path('api/shipping-price/', category_views.shipping_price_api, name='shipping_price_api'),
    # Add Django's authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='account_login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='account_logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
