from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import generics, permissions
from .models import Feedback, Order
from .serializers import FeedbackSerializer, OrderSerializer
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
from .models import PickupRequest

from rest_framework import views
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
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
    # permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def post(self, request):
        serializer = QuoteSerializer(data = request.data)
        if serializer.is_valid():
            shipping_route = serializer.validated_data["shipping_route"]
            type = serializer.validated_data["type"]
            weight = serializer.validated_data["weight"]
            weight_metric = serializer.validated_data["weight_metric"]
            dim_length = serializer.validated_data["dim_length"]
            dim_width = serializer.validated_data["dim_width"]
            dim_height = serializer.validated_data["dim_height"]
            usd_rate = serializer.validated_data["usd_rate"]

            if weight_metric == "lb":
                weight *= 0.453592

            volumetric_weight = (dim_length * dim_width * dim_height) / 5000

            chargeable_weight = max(volumetric_weight, weight)

            base_price = chargeable_weight * 1000
            route_multiplier = 1.5 if shipping_route == "india-to-usa" else 2.5
            package_multiplier = 1.0 if type == "document" else 1.5
            inr_price = math.ceil(base_price * route_multiplier * package_multiplier)
            usd_price = math.ceil(inr_price / usd_rate)

            shipping_time = "10-15 business days" if shipping_route == "india-to-usa" else "7-10 business days"

            return Response({
                "inr_price": inr_price, 
                "usd_price": usd_price, 
                "chargeable_Weight": chargeable_weight, 
                "shipping_time": shipping_time
            })
        return Response(serializer.errors, status=400)


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


# class FeedbackViewSet(viewsets.ModelViewSet):
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("Serializer Errors:", serializer.errors)  # 🔴 This will print the actual reason
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]