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
from django.conf import settings
from django.conf.urls.static import static

from django.views.decorators.csrf import csrf_exempt
from .views import (
    QuoteView, GenerateQuotePDF,
    OrderViewSet, FeedbackViewSet,
    UserViewSet, AddressViewSet,
    ShipmentViewSet, BillViewSet,
    InvoiceViewSet, PickupRequestViewSet,
    SupportRequestViewSet, api_root
)

# DRF Router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'shipments', ShipmentViewSet, basename='shipment')
router.register(r'bills', BillViewSet, basename='bill')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'pickup-requests', PickupRequestViewSet, basename='pickuprequest')
router.register(r'support-requests', SupportRequestViewSet, basename='supportrequest')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

# Schema View for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="ParcelMyBox API",
        default_version='v1',
        description="""
        <h2>ParcelMyBox Shipping Management System API</h2>
        <p>This API provides endpoints for managing orders and feedback.</p>
        """,
        terms_of_service="https://www.parcelmybox.com/terms/",
        contact=openapi.Contact(email="support@parcelmybox.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# URL patterns
urlpatterns = [
    path('', api_root, name='api-root'),

    # DRF router endpoints
    path('', include(router.urls)),

    # Quote-related endpoints
    path('quotes/', QuoteView.as_view(), name='quote-calculate'),
    path('quote/', QuoteView.as_view(), name='quote'),
    path('generate-quote-pdf/', GenerateQuotePDF.as_view(), name='generate_quote_pdf'),

    # JWT Auth endpoints
    path('auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),

    # API documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Browsable API auth
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Static and media file serving (for development only)
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
