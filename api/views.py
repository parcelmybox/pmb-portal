from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone
from shipping.models import Shipment, ShippingAddress, Bill, Invoice, ShipmentItem, TrackingEvent, SupportRequest
from .serializers import (
    UserSerializer, ShipmentSerializer, 
    ShippingAddressSerializer, BillSerializer, InvoiceSerializer,
    ShipmentItemSerializer, TrackingEventSerializer, ContactSerializer, PickupRequestSerializer,
    QuoteSerializer, SupportRequestSerializer,
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly

from rest_framework import generics
from .models import PickupRequest, ShippingRates

from rest_framework import views
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
import datetime
import math

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'username'  # Use username instead of ID for lookups

    def get_queryset(self):
        # Regular users can only see their own profile
        if not self.request.user.is_staff:
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()
    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        user = request.user
        # Dummy values to simulate – later query from related models
        data = {
            "name": user.get_full_name(),
            "email": user.email,
            "phone": getattr(user, 'phone', 'N/A'),  # if you have a phone field
            "locker_code": f"PMB-{user.id:04}",
            "warehouse_address": "15914 Brownstone Ave, Lathrop, CA",
            "total_pickups": Shipment.objects.filter(sender_address__user=user).count(),
            "total_bills": Bill.objects.filter(customer=user).count()
        }
        return Response(data)
    
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    queryset = ShippingAddress.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'city', 'state', 'country', 'postal_code']
    ordering_fields = ['is_default', 'city', 'state', 'country']

    def get_queryset(self):
        # Users can only see their own addresses
        return ShippingAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the address with the current user
        serializer.save(user=self.request.user)
        
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()
        # Set this address as default and unset others
        ShippingAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'status': 'default address set'})

class ShipmentViewSet(viewsets.ModelViewSet):
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'tracking_number', 
        'sender_address__first_name', 'sender_address__last_name',
        'recipient_address__first_name', 'recipient_address__last_name',
        'status'
    ]
    ordering_fields = ['shipping_date', 'delivery_date', 'created_at', 'updated_at']

    def get_queryset(self):
        # Users can see shipments where they are either sender or recipient
        return Shipment.objects.filter(
            models.Q(sender_address__user=self.request.user) |
            models.Q(recipient_address__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        # Automatically set the sender address user if not set
        sender_address = serializer.validated_data.get('sender_address')
        if sender_address and not sender_address.user:
            sender_address.user = self.request.user
            sender_address.save()
        serializer.save()

    @action(detail=True, methods=['post'])
    def generate_bill(self, request, pk=None):
        shipment = self.get_object()
        try:
            bill = shipment.generate_bill(created_by=request.user)
            return Response({
                "status": "Bill generated successfully",
                "bill_id": bill.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def generate_invoice(self, request, pk=None):
        shipment = self.get_object()
        try:
            invoice = shipment.generate_invoice(created_by=request.user)
            return Response({
                "status": "Invoice generated successfully",
                "invoice_id": invoice.id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def tracking_events(self, request, pk=None):
        """Get tracking events for a shipment"""
        shipment = self.get_object()
        events = shipment.tracking_events.all().order_by('timestamp')
        serializer = TrackingEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get items in a shipment"""
        shipment = self.get_object()
        items = shipment.items.all()
        serializer = ShipmentItemSerializer(items, many=True)
        return Response(serializer.data)

class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'customer__username', 'customer__email',
        'shipment__tracking_number', 'status',
        'payment_method'
    ]
    ordering_fields = ['due_date', 'created_at', 'paid_at']

    def get_queryset(self):
        # Users can see their own bills or bills they created
        return Bill.objects.filter(
            models.Q(customer=self.request.user) |
            models.Q(created_by=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        # Set the customer to the current user if not provided
        if 'customer' not in serializer.validated_data:
            serializer.save(customer=self.request.user, created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        bill = self.get_object()
        payment_method = request.data.get('payment_method', 'CASH')
        try:
            bill.mark_as_paid(payment_method=payment_method)
            return Response({"status": "Bill marked as paid"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'customer__username', 'customer__email',
        'shipment__tracking_number', 'status',
        'invoice_number'
    ]
    ordering_fields = ['due_date', 'created_at', 'paid_at']

    def get_queryset(self):
        # Users can see their own invoices or invoices they created
        return Invoice.objects.filter(
            models.Q(customer=self.request.user) |
            models.Q(created_by=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        # Set the customer to the current user if not provided
        if 'customer' not in serializer.validated_data:
            serializer.save(customer=self.request.user, created_by=self.request.user)
        else:
            serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        invoice = self.get_object()
        payment_method = request.data.get('payment_method', 'CASH')
        try:
            invoice.mark_as_paid(payment_method=payment_method)
            return Response({"status": "Invoice marked as paid"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Generate and return a PDF version of the invoice"""
        invoice = self.get_object()
        # This would typically generate and return a PDF file
        # For now, we'll just return a success message
        return Response({
            "status": "PDF generation would happen here",
            "invoice_id": invoice.id
        })

# Quote Calculation API

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
            usd_rate = serializer.validated_data["usd_rate"]
            carrier_preference_type = serializer.validated_data["carrier_preference_type"]
            carrier_preference = serializer.validated_data["carrier_preference"]

            chargeable_weight = 0
            prices = []
            volumetric_used = False
            shipping_time = "10-15 business days" if shipping_route == "india-to-usa" else "7-10 business days"

            if type == "package":
                if weight_metric == "lb":
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
                    prices.append({
                        "fixed_price": price.fixed_price,
                        "per_kg_price": price.per_kg_price,
                        "courier_name": price.courier
                    })
            else:
                relevant_prices = ShippingRates.objects.filter(min_kg__lte = weight, max_kg__gte = weight, package_type=type)
                prices.append({
                    "fixed_price": relevant_prices[0].fixed_price,
                    "per_kg_price": relevant_prices[0].per_kg_price,
                    "courier_name": ""
                })
            
            return Response({
                "prices": prices, 
                "chargeable_weight": chargeable_weight if chargeable_weight else weight,
                "shipping_time": shipping_time,
                "volumetric_used": volumetric_used,
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

            # Generate Invoice ID and Date
            invoice_id = f"QUOTE-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            quote_date = datetime.datetime.now().strftime("%B %d, %Y")

            for price in quote_data.get('prices'):
                print(f"{price.get('courier_name')} {carrier_preference} {price.get('courier_name') == carrier_preference}")
                if price.get("courier_name") == carrier_preference:
                    if price.get("fixed_price") is None:
                        base_price = float(price.get("per_kg_price", 0)) * float(quote_data.get("chargeableWeight", 0))
                    else:
                        base_price = int(price.get("fixed_price"))

            # Combine data for template
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
                "base_price": f"{form_data.get('currency', '')}{base_price}",
                "currency": form_data.get("currency", "₹"),
                "exchange_rate": f"1 USD = ₹{form_data.get('usdRate', '')}",
                "dimensions": (
                    f"{form_data['dim_length']}L{form_data['dim_width']}W{form_data['dim_height']}H"
                    if form_data.get("dim_length") else "N/A"
                )
            }

            # Render HTML template
            template = get_template('api/quote-pdf-template-temp.html')
            html = template.render(context)

            # Create HTTP response with PDF headers
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{invoice_id}.pdf"'

            try:
                # Generate PDF using xhtml2pdf
                from xhtml2pdf import pisa

                # Simple CSS to ensure basic formatting
                default_css = """
                    body {
                        font-family: Arial, sans-serif;
                        font-size: 10px;
                        line-height: 1.4;
                        margin: 0;
                        padding: 0;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 10px 0;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 6px;
                        text-align: left;
                    }
                    th {
                        background-color: #f5f5f5;
                        font-weight: bold;
                    }
                """

                pisa_status = pisa.CreatePDF(
                    html,
                    dest=response,
                    encoding='UTF-8',
                    link_callback=None,
                    show_error_as_pdf=False,
                    xhtml=False,
                    default_css=default_css
                )

                if pisa_status.err:
                    return Response(
                        {"error": "Failed to generate PDF"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                return response

            except Exception as e:
                return Response({"error": f"PDF generation error: {str(e)}"}, status=500)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

#pickupRequest

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PickupRequest
from .serializers import PickupRequestSerializer

class SupportRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows support requests to be viewed or edited.
    """
    serializer_class = SupportRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket_number', 'subject', 'message', 'status']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        This view should return a list of all support requests
        for the currently authenticated user, or all requests for staff users.
        """
        user = self.request.user
        if user.is_staff:
            return SupportRequest.objects.all()
        return SupportRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        # Automatically set the user to the current user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Custom action to update the status of a support request.
        """
        support_request = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'status': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if new_status not in dict(SupportRequest.STATUS_CHOICES).keys():
            return Response(
                {'status': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        support_request.status = new_status
        support_request.save()
        
        return Response({'status': 'Status updated successfully'})

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """
        Add a resolution note to a support request.
        """
        support_request = self.get_object()
        note = request.data.get('note')
        
        if not note:
            return Response(
                {'error': 'Note is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if support_request.resolution_notes:
            support_request.resolution_notes += f"\n\n{timezone.now().strftime('%Y-%m-%d %H:%M')} - {note}"
        else:
            support_request.resolution_notes = f"{timezone.now().strftime('%Y-%m-%d %H:%M')} - {note}"
            
        support_request.save()
        return Response({'status': 'Note added successfully'})

class PickupRequestViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for PickupRequests
    """
    serializer_class = PickupRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show requests belonging to current user"""
        return PickupRequest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Auto-set user on creation"""
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        """Auto-update without changing user"""
        serializer.save()