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
from .views import QuoteView, OrderViewSet, FeedbackViewSet

# DRF Router
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

# Swagger/OpenAPI schema view
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
    # Core API routes
    path('', include(router.urls)),

    # Quote endpoint
    path('quote/', QuoteView.as_view(), name='quote'),

    # Auth endpoints (JWT)
    path('auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),

    # Swagger & ReDoc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Browsable API login/logout
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Static and media file serving in development
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
