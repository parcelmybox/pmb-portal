"""
URL configuration for pmb_hello project.

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
from category import views as category_views
from . import views as pmb_hello_views
from shipping import admin as shipping_admin  # Import our custom admin site

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
    path('', pmb_hello_views.site_home_page, name='site_home_page'),  # Site home page
    path('admin/logout/', admin_logout, name='admin-logout'),  # Admin logout - Fixed the URL name to avoid ':'
    path('admin/', shipping_admin.site.urls),  # Use our custom admin site
    
    # Shipping app URLs and redirects
    path('shipping/', include('shipping.urls')),
    
    # Redirect old pricing URL to new one
    path('shipping/pricing/', RedirectView.as_view(url='/shipping-price/', permanent=True)),
    # Redirect old billing URLs to new ones
    path('admin/shipping/bill/', RedirectView.as_view(url='/shipping/bills/', permanent=True)),
    path('admin/shipping/bill/add/', RedirectView.as_view(url='/shipping/bills/create/', permanent=True)),
    path('categories/', category_views.category_list, name='category_list'),
    path('shipping-price/', category_views.shipping_price_form, name='shipping_price_form'),
    path('api/shipping-price/', category_views.shipping_price_api, name='shipping_price_api'),
    # Add Django's authentication URLs
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
