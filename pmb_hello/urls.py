"""
URL configuration for pmb_hello project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from category import views as category_views
from . import views as pmb_hello_views
from shipping import admin as shipping_admin  # Custom admin

# Auth logout
from django.contrib.auth.views import LogoutView
from django.views.decorators.http import require_http_methods

# ✅ Swagger imports
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ✅ Swagger schema setup
schema_view = get_schema_view(
    openapi.Info(
        title="ParcelMyBox API",
        default_version='v1',
        description="API documentation for ParcelMyBox backend",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Admin logout function
@require_http_methods(["GET", "POST"])
def admin_logout(request):
    from django.contrib.auth import logout
    from django.http import HttpResponseRedirect
    from django.urls import reverse
    from django.contrib import messages

    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return HttpResponseRedirect(reverse('admin:login'))


# ✅ Final urlpatterns
urlpatterns = [
    # ✅ Directly include API URLs (fixes /api/auth/token/)
    path('api/', include('api.urls')),

    # ✅ Swagger & Redoc documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Redirect for easy docs access
    path('api/docs/', RedirectView.as_view(url='/api/swagger/', permanent=False), name='api-docs'),

    # Main frontend routes
    path('', pmb_hello_views.site_home_page, name='site_home_page'),

    # Admin & logout
    path('admin/logout/', admin_logout, name='admin-logout'),
    path('admin/', shipping_admin.site.urls),

    # Shipping app
    path('shipping/', include('shipping.urls')),

    # Old URL redirects
    path('shipping/pricing/', RedirectView.as_view(url='/shipping-price/', permanent=True)),
    path('admin/shipping/bill/', RedirectView.as_view(url='/shipping/bills/', permanent=True)),
    path('admin/shipping/bill/add/', RedirectView.as_view(url='/shipping/bills/create/', permanent=True)),

    # Category & pricing
    path('categories/', category_views.category_list, name='category_list'),
    path('shipping-price/', category_views.shipping_price_form, name='shipping_price_form'),
    path('api/shipping-price/', category_views.shipping_price_api, name='shipping_price_api'),

    # Auth
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
