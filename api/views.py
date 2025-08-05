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



class QuoteView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = QuoteSerializer(data = request.data)
        if serializer.is_valid():
            shipping_route = serializer.validated_data["shipping_route"]
            type = serializer.validated_data["type"]
            weight = serializer.validated_data["weight"]
            weight_metric = serializer.validated_data["weight_metric"]
            include_dimensions = serializer.validated_data["include_dimensions"]
            dim_length = serializer.validated_data["dim_length"]
            dim_width = serializer.validated_data["dim_width"]
            dim_height = serializer.validated_data["dim_height"]
            currency = serializer.validated_data['currency']
            usd_rate = serializer.validated_data["usd_rate"]

            chargeable_weight = 0
            prices = []
            volumetric_used = False
            shipping_time = "10-15 business days" if shipping_route == "india-to-usa" else "7-10 business days"
            if type == "package":
                if weight_metric == "lbs":
                    weight *= 0.453592

                if include_dimensions:
                    volumetric_weight = (dim_length * dim_width * dim_height) / 5000
                    if volumetric_weight > weight:
                        chargeable_weight = math.ceil(volumetric_weight)
                        volumetric_used = True
                    else: chargeable_weight = math.ceil(weight)
                else: chargeable_weight = math.ceil(weight)

                relevant_prices = ShippingRates.objects.filter(min_kg__lte = chargeable_weight, max_kg__gte = chargeable_weight, package_type=type)
                for price in relevant_prices:
                    if price.courier == "ups": price.courier = "UPS Shipping"
                    elif price.courier == "dhl": price.courier = "DHL Shipping"
                    elif price.courier == "fedex": price.courier = "FedEx Shipping"

                    if currency == '$':
                        if price.fixed_price: price.fixed_price = math.ceil(float(price.fixed_price) / usd_rate)
                        elif price.per_kg_price: price.per_kg_price = math.ceil(float(price.per_kg_price) / usd_rate)
                    
                    prices.append({
                        "fixed_price": price.fixed_price,
                        "per_kg_price": price.per_kg_price,
                        "courier_name": price.courier,
                    })
            else:
                relevant_prices = ShippingRates.objects.filter(min_kg__lte = weight, max_kg__gte = weight, package_type=type)
                if currency == '$':
                    for price in relevant_prices:
                        price.fixed_price = math.ceil(float(price.fixed_price) / usd_rate)
                prices.append({
                    "fixed_price": relevant_prices[0].fixed_price,
                    "per_kg_price": relevant_prices[0].per_kg_price,
                    "courier_name": "UPS Shipping",
                })
            
            return Response({
                "prices": prices, 
                "chargeable_weight": chargeable_weight if chargeable_weight else weight,
                "shipping_time": shipping_time,
                "volumetric_used": volumetric_used,
                "currency": currency,
            })
        return Response(serializer.errors, status=400)

class GenerateQuotePDF(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data
            form_data = data.get("formData")
            quote_data = data.get("quoteData")
            carrier_preference = data.get("carrierPreference")

            invoice_id = f"QUOTE-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            quote_date = datetime.datetime.now().strftime("%B %d, %Y")

            base_price = 0
            for price in quote_data.get('prices'):
                if price.get("courier_name") == carrier_preference:
                    if price.get("fixed_price") is None:
                        base_price = float(price.get("per_kg_price", 0)) * float(quote_data.get("chargeableWeight", 0))
                    else:
                        base_price = int(price.get("fixed_price"))

            context = {
                "invoice_id": invoice_id,
                "quote_date": quote_date,
                "shipping_route": form_data.get("shippingRoute", ""),
                "origin_city": form_data.get("originCity", ""),
                "destination_city": form_data.get("destinationCity", ""),
                "package_type": form_data.get("packageType", ""),
                "weight": form_data.get("weight", 0),
                "weight_unit": form_data.get("weightUnit", ""),
                "chargeable_weight": quote_data.get("chargeableWeight", 0),
                "volumetric_used": quote_data.get("volumetricUsed", False),
                "shipping_time": quote_data.get("shippingTime", ""),
                "carrier_name": carrier_preference,
                "base_price": f"{quote_data.get('currency', '₹')}{base_price}",
                "currency": quote_data.get("currency", "₹"),
                "exchange_rate": f"1$ = ₹{data.get('usdRate', '')}",
                "dimensions": (
                    f"{form_data['dim_length']}L{form_data['dim_width']}W{form_data['dim_height']}H"
                    if form_data.get("dim_length") else "N/A"
                )
            }

            # Render HTML using Django template
            template = get_template('api/quote-pdf-template.html')
            html_content = template.render(context)

            # Generate PDF with pdfkit
            options = {
                'encoding': "UTF-8",
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
            }

            pdf_file = pdfkit.from_string(html_content, False, options=options)

            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{invoice_id}.pdf"'
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=400)