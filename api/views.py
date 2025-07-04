from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from .models import SupportRequest
from .serializers import SupportRequestSerializer
from django.db import models
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from shipping.models import Shipment, ShippingAddress, Bill, Invoice, ShipmentItem, TrackingEvent
from .serializers import (
    UserSerializer, ShipmentSerializer, 
    ShippingAddressSerializer, BillSerializer, InvoiceSerializer,
    ShipmentItemSerializer, TrackingEventSerializer, ContactSerializer,PickupRequestSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly

from rest_framework import generics
from .models import PickupRequest



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


#pickupRequest

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PickupRequest
from .serializers import PickupRequestSerializer

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
class SupportRequestViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for support requests
    """
    serializer_class = SupportRequestSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        """Only show requests submitted by the current user"""
        return SupportRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Auto-set the user on creation"""
        serializer.save(user=self.request.user)
