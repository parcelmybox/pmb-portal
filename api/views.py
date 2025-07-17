from django.shortcuts import render
from rest_framework import viewsets, status, filters, generics, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone
import random

from .models import SupportRequest, PickupRequest
from .serializers import (
    UserSerializer, ShipmentSerializer, 
    ShippingAddressSerializer, BillSerializer, InvoiceSerializer,
    ShipmentItemSerializer, TrackingEventSerializer, ContactSerializer, 
    PickupRequestSerializer, QuoteSerializer, SupportRequestSerializer,
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly
from shipping.models import (
    Shipment, ShippingAddress, Bill, Invoice, 
    ShipmentItem, TrackingEvent, SupportRequest as ShippingSupportRequest
)

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
    Unauthenticated users can create support requests.
    Authenticated users can view their own requests.
    Staff users can view and manage all requests.
    """
    serializer_class = SupportRequestSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated creation
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket_number', 'subject', 'message', 'status', 'email']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser]  # For file uploads

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        elif self.action == 'create':
            permission_classes = [AllowAny]  # Anyone can create a support request
        else:
            permission_classes = [IsAdminUser]  # Only admin for custom actions
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Returns support requests based on user role:
        - Staff: Can see all requests
        - Authenticated users: Can see requests associated with their email
        - Anonymous: No access
        """
        user = self.request.user
        queryset = SupportRequest.objects.all()
        
        if user.is_staff:
            # Staff can see all requests
            return queryset
            
        if user.is_authenticated:
            # Regular users can see requests with their email
            return queryset.filter(email=user.email)
            
        return SupportRequest.objects.none()

    def create(self, request, *args, **kwargs):
        print("\n=== Support Request Data ===")
        print("Request data:", request.data)
        print("Request user:", request.user if request.user.is_authenticated else 'Anonymous')
        print("Request files:", dict(request.FILES) if hasattr(request, 'FILES') else 'No files')
        
        # Log the raw request data before validation
        print("\n=== Raw Request Data ===")
        for key, value in request.data.items():
            print(f"{key}: {value} ({type(value)})")
            
        # Log the raw POST data
        print("\n=== Raw POST Data ===")
        print(request.POST)
        
        try:
            # Log the data being passed to the serializer
            print("\n=== Data being passed to serializer ===")
            print(request.data)
            
            # Manually validate the serializer first to get detailed errors
            serializer = self.get_serializer(data=request.data)
            is_valid = serializer.is_valid(raise_exception=False)
            
            if not is_valid:
                print("\n=== Validation Errors ===")
                print(serializer.errors)
                
            print("\n=== Validated Data ===")
            print(serializer.validated_data)
            
            # If validation passes, proceed with creation
            self.perform_create(serializer)
            print("\n=== After perform_create ===")
            print("Saved object:", serializer.instance)
            print("Request type in instance:", getattr(serializer.instance, 'request_type', 'Not set'))
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            print("\n=== Validation Error ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            if hasattr(e, 'detail'):
                print(f"Error detail: {e.detail}")
            if hasattr(e, 'get_codes'):
                print(f"Error codes: {e.get_codes()}")
            
            # Re-raise the exception to maintain the same behavior
            raise

    def get_random_staff_member(self):
        """
        Returns a random active staff member to assign to the support request.
        Returns None if no staff members are available.
        """
        staff_members = get_user_model().objects.filter(
            is_staff=True,
            is_active=True
        )
        
        if staff_members.exists():
            return random.choice(staff_members)
        return None
    
    def perform_create(self, serializer):
        """
        Auto-set the created_by if user is authenticated.
        Assign a random staff member to the support request.
        """
        print("\n=== Performing Create ===")
        print("Raw serializer data:", serializer.validated_data)
        
        # Log the request data being used for creation
        print("\n=== Request Data ===")
        print("Request data:", self.request.data)
        print("Request POST:", self.request.POST)
        print("Request FILES:", dict(self.request.FILES) if hasattr(self.request, 'FILES') else 'No files')
        
        # Log the request type specifically
        request_type = self.request.data.get('category') or self.request.data.get('request_type')
        print(f"\n=== Request Type Debug ===")
        print(f"Category from request: {self.request.data.get('category')}")
        print(f"Request type from request: {self.request.data.get('request_type')}")
        print(f"Using request type: {request_type}")
        
        # Get a random staff member to assign
        assigned_to = self.get_random_staff_member()
        print(f"\n=== Staff Assignment Debug ===")
        print(f"Found staff member to assign: {assigned_to}")
        if assigned_to:
            print(f"Staff details - ID: {assigned_to.id}, Username: {assigned_to.username}")
        
        # Prepare save kwargs
        save_kwargs = {}
        
        # Set created_by if user is authenticated
        if self.request.user.is_authenticated:
            print("User is authenticated, setting created_by")
            save_kwargs['created_by'] = self.request.user
        
        # Always set assigned_to if a staff member is available
        if assigned_to:
            print(f"Assigning to staff member: {assigned_to.username} (ID: {assigned_to.id})")
            save_kwargs['assigned_to_id'] = assigned_to.id  # Use _id to bypass any potential model validation
        else:
            print("Warning: No active staff members available for assignment")
        
        # Ensure request_type is set in the validated data
        if request_type and 'request_type' not in serializer.validated_data:
            print(f"Setting request_type to {request_type} from request data")
            serializer.validated_data['request_type'] = request_type
        
        # Save with the collected kwargs
        print("\n=== Final Save Data ===")
        print(f"Validated data: {serializer.validated_data}")
        print(f"Save kwargs: {save_kwargs}")
        
        instance = serializer.save(**save_kwargs)
        
        # Verify the saved data
        print("\n=== After Save ===")
        print(f"Instance ID: {instance.id}")
        print(f"Saved request_type: {instance.request_type}")
        print(f"Saved category: {getattr(instance, 'category', 'N/A')}")
        
        # Verify the assignment was saved
        if hasattr(instance, 'assigned_to'):
            print(f"After save - Assigned to: {instance.assigned_to}")
        else:
            print("After save - No assigned_to field on instance")

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def update_status(self, request, pk=None):
        """
        Custom action to update the status of a support request.
        Only accessible by admin users.
        """
        instance = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'status': 'Status is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        instance.status = new_status
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminUser])
    def add_note(self, request, pk=None):
        """
        Add a resolution note to a support request.
        Only accessible by admin users.
        """
        instance = self.get_object()
        note = request.data.get('note')
        
        if not note:
            return Response(
                {'note': 'This field is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not instance.resolution_notes:
            instance.resolution_notes = note
        else:
            instance.resolution_notes = f"{instance.resolution_notes}\n\n{note}"
            
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class PickupRequestViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for PickupRequests.
    Users can only access their own pickup requests.
    """
    serializer_class = PickupRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['pickup_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Only show requests belonging to current user
        return PickupRequest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Auto-set user on creation
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        # Auto-update without changing user
        serializer.save()