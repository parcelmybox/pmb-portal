from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from .views import QuoteView

from . import views
from django.conf.urls.static import static

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'shipments', views.ShipmentViewSet, basename='shipment')
router.register(r'bills', views.BillViewSet, basename='bill')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'pickup-requests', views.PickupRequestViewSet, basename='pickuprequest')
router.register(r'support-requests', views.SupportRequestViewSet, basename='supportrequest')
# Schema View for API documentation
schema_view = get_schema_view(
   openapi.Info(
      title="ParcelMyBox API",
      default_version='v1',
      description="""
      <h2>ParcelMyBox Shipping Management System API</h2>
      <p>This API provides endpoints for managing shipments, addresses, bills, invoices and pickup request</p>
      <p>To get started, obtain an access token by authenticating with your credentials.</p>
      """,
      terms_of_service="https://www.parcelmybox.com/terms/",
      contact=openapi.Contact(email="support@parcelmybox.com"),
      license=openapi.License(name="Proprietary"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # Custom API root view
    path('', views.api_root, name='api-root'),
    
    # Include router URLs
    path('', include(router.urls)),
    
    # Quote calculation endpoint
    path('quotes/', QuoteView.as_view(), name='quote-calculate'),
    
    # Authentication endpoints
    path('auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    
    # API documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', 
            schema_view.without_ui(cache_timeout=0), 
            name='schema-json'),
    path('swagger/', 
         schema_view.with_ui('swagger', cache_timeout=0), 
         name='schema-swagger-ui'),
    path('redoc/', 
         schema_view.with_ui('redoc', cache_timeout=0), 
         name='schema-redoc'),
    
    # Browsable API login/logout
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Add debug toolbar and serve media files in development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        # Debug toolbar is not installed, skip it
        pass
        
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Removed the duplicate and misplaced code
