from django.shortcuts import render
from rest_framework import viewsets, status, filters, generics, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination
import json

class PrettyJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that formats the output with indentation and newlines
    for better readability in the browser.
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if self.charset is None:
            self.charset = 'utf-8'
            
        try:
            # Format the main response dictionary
            formatted_data = json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                default=str
            )
            
            # Add extra newlines between items in the results array
            if isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
                formatted_data = formatted_data.replace('},', '},\n\n')
            
            # Ensure we return bytes with proper encoding
            if isinstance(formatted_data, str):
                return formatted_data.encode(self.charset)
            return formatted_data
            
        except Exception as e:
            # Fall back to default renderer if there's an error
            return super().render(data, accepted_media_type, renderer_context)


class SupportRequestPagination(PageNumberPagination):
    """
    Custom pagination class for support requests that uses the pretty JSON renderer
    and adds some custom pagination headers.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    renderer_classes = [PrettyJSONRenderer]
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models import Q
from django.utils import timezone
import random

from .models import SupportRequest, PickupRequest
from .serializers import (
    UserSerializer, ShipmentSerializer, 
    ShippingAddressSerializer, BillSerializer, InvoiceSerializer,
    ShipmentItemSerializer, TrackingEventSerializer, ContactSerializer, 
    PickupRequestSerializer, QuoteSerializer, SupportRequestSerializer, SupportRequestListSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly
from shipping.models import (
    Shipment, ShippingAddress, Bill, Invoice, 
    ShipmentItem, TrackingEvent, SupportRequest as ShippingSupportRequest
)

import math

User = get_user_model()

class APIRootView(APIView):
    """
    ## ParcelMyBox API
    
    Welcome to the ParcelMyBox API. This API provides endpoints for managing shipments,
    addresses, bills, invoices, and support requests.
    
    ### Authentication
    - Obtain an access token using `/auth/token/`
    - Include the token in the `Authorization: Bearer <token>` header
    
    ### Available Endpoints
    """
    
    def get(self, request, format=None):
        data = {
            'admin': {
                'url': reverse('admin:index', request=request, format=format),
                'description': 'Django admin interface',
                'methods': ['GET']
            },
            'users': {
                'url': reverse('user-list', request=request, format=format),
                'description': 'User management endpoints',
                'methods': ['GET', 'POST']
            },
            'addresses': {
                'url': reverse('address-list', request=request, format=format),
                'description': 'Shipping address management',
                'methods': ['GET', 'POST']
            },
            'shipments': {
                'url': reverse('shipment-list', request=request, format=format),
                'description': 'Shipment management and tracking',
                'methods': ['GET', 'POST']
            },
            'bills': {
                'url': reverse('bill-list', request=request, format=format),
                'description': 'Billing information',
                'methods': ['GET', 'POST']
            },
            'invoices': {
                'url': reverse('invoice-list', request=request, format=format),
                'description': 'Invoice management',
                'methods': ['GET', 'POST']
            },
            'pickup-requests': {
                'url': reverse('pickuprequest-list', request=request, format=format),
                'description': 'Schedule and manage package pickups',
                'methods': ['GET', 'POST']
            },
            'support-requests': {
                'url': reverse('supportrequest-list', request=request, format=format),
                'description': 'Customer support ticket system',
                'methods': ['GET', 'POST']
            },
            'auth': {
                'token': {
                    'obtain': reverse('token_obtain_pair', request=request, format=format),
                    'refresh': reverse('token_refresh', request=request, format=format),
                    'verify': reverse('token_verify', request=request, format=format)
                },
                'description': 'Authentication endpoints',
                'methods': ['POST']
            },
            'documentation': {
                'swagger': reverse('schema-swagger-ui', request=request, format=format),
                'redoc': reverse('schema-redoc', request=request, format=format),
                'description': 'Interactive API documentation',
                'methods': ['GET']
            }
        }
        return Response(data)

# Create an instance of the view
api_root = APIRootView.as_view()


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
    permission_classes = [AllowAny]  # Allow unauthenticated access for creating support requests
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket_number', 'subject', 'message', 'status', 'email']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = SupportRequestPagination
    renderer_classes = [PrettyJSONRenderer, renderers.BrowsableAPIRenderer]
    
    def get_serializer_class(self):
        """
        Use different serializers for list vs. detail views.
        """
        if self.action == 'list':
            return SupportRequestListSerializer
        return SupportRequestSerializer
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        elif self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Returns support requests based on user role:
        - Staff: Can see all requests
        - Authenticated users: Can see requests that match their email
        - Anonymous: No access
        """
        user = self.request.user
        
        # Use the correct model from shipping app
        from shipping.models import SupportRequest as ShippingSupportRequest
        queryset = ShippingSupportRequest.objects.all()
        
        # Debug information
        print("\n=== DEBUG: get_queryset ===")
        print(f"[USER] ID: {user.id}, Username: {user.username}")
        print(f"[AUTH] is_authenticated: {user.is_authenticated}, is_staff: {getattr(user, 'is_staff', False)}")
        print(f"[EMAIL] {getattr(user, 'email', 'No email')}")
        print(f"[QUERY] Total support requests in DB: {queryset.count()}")
        
        # Debug: Print all support requests
        if queryset.exists():
            print("\n=== ALL SUPPORT REQUESTS ===")
            for req in queryset.order_by('-created_at')[:5]:
                print(f"ID: {req.id}, Email: {req.email or 'None'}, Subject: {req.subject}, Status: {req.status}, Created: {req.created_at}")
        else:
            print("\n[DEBUG] No support requests found in the database")
        
        if user.is_staff:
            # Staff can see all requests
            print("\n[DEBUG] User is staff, returning all support requests")
            return queryset.order_by('-created_at')
            
        if user.is_authenticated and hasattr(user, 'email') and user.email:
            # Regular users can see requests that match their email
            filtered = queryset.filter(email=user.email).order_by('-created_at')
            print(f"\n[DEBUG] Found {filtered.count()} support requests for email: {user.email}")
            return filtered
            
        print("\n[DEBUG] User not authenticated or has no email, returning no support requests")
        return ShippingSupportRequest.objects.none()

    def get_random_staff_member(self):
        """
        Returns a random active staff member to assign to the support request.
        Returns None if no staff members are available.
        """
        from django.db.models import Count, Q
        
        # First try to find staff with the fewest open/in-progress tickets
        staff_members = get_user_model().objects.filter(
            is_staff=True,
            is_active=True
        ).annotate(
            ticket_count=Count('assigned_support_requests', 
                            filter=Q(assigned_support_requests__status__in=['open', 'in_progress']))
        ).order_by('ticket_count')
        
        if staff_members.exists():
            # Get the first staff member with the fewest tickets
            return staff_members.first()
            
        # Fallback to any active staff member
        staff = get_user_model().objects.filter(
            is_staff=True,
            is_active=True
        ).order_by('?').first()
        
        if staff:
            return staff
            
        # Last resort: get any active superuser
        return get_user_model().objects.filter(
            is_superuser=True,
            is_active=True
        ).first()
        
    def create(self, request, *args, **kwargs):
        print("\n=== Support Request Data ===")
        print("Request data:", request.data)
        print("Request user:", request.user if request.user.is_authenticated else 'Anonymous')
        print("Request files:", dict(request.FILES) if hasattr(request, 'FILES') else 'No files')
        
        # Handle unauthenticated requests with invalid tokens
        if not request.user.is_authenticated:
            # Remove any Authorization header that might cause issues
            if 'HTTP_AUTHORIZATION' in request.META:
                auth_header = request.META['HTTP_AUTHORIZATION']
                if auth_header.startswith('Bearer null') or 'null' in auth_header:
                    print("Removing invalid Authorization header with null token")
                    del request.META['HTTP_AUTHORIZATION']
                elif not auth_header.startswith('Bearer '):
                    print("Removing malformed Authorization header")
                    del request.META['HTTP_AUTHORIZATION']
            
            # Ensure the request is treated as unauthenticated
            request._force_auth_user = None
            request.user = AnonymousUser()
        
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
            
            # Force validation and capture all errors
            is_valid = serializer.is_valid(raise_exception=False)
            
            if not is_valid:
                print("\n=== Detailed Validation Errors ===")
                print(serializer.errors)
                print("\n=== Raw Data ===")
                print(f"Name: {request.data.get('name')}")
                print(f"Contact: {request.data.get('contact')}")
                print(f"Category: {request.data.get('category')}")
                print(f"Subject: {request.data.get('subject')}")
                print(f"Message: {request.data.get('message')}")
                print("\n=== Validated Data (partial) ===")
                print(serializer.validated_data)
                
                # Return the validation errors to the client
                return Response(
                    {"detail": "Validation failed", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
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
        import random
        from django.db.models import Count, Q
        
        # First try to get staff with the fewest open/in-progress tickets
        staff_members = get_user_model().objects.filter(
            is_staff=True,
            is_active=True
        ).annotate(
            ticket_count=Count('assigned_support_requests', 
                            filter=Q(assigned_support_requests__status__in=['open', 'in_progress']))
        ).order_by('ticket_count')
        
        if staff_members.exists():
            # Get all staff with the minimum number of tickets
            min_tickets = staff_members.first().ticket_count
            candidates = list(staff_members.filter(ticket_count=min_tickets))
            
            # If we have multiple candidates with the same minimum tickets, choose randomly
            if len(candidates) > 1:
                return random.choice(candidates)
            return candidates[0]
            
        # Fallback to any active staff member if no tickets exist yet
        staff = get_user_model().objects.filter(
            is_staff=True,
            is_active=True
        ).order_by('?').first()
        
        if staff:
            return staff
            
        # Last resort: get any active superuser
        return get_user_model().objects.filter(
            is_superuser=True,
            is_active=True
        ).first()
    
    def perform_create(self, serializer):
        """
        Auto-set the created_by if user is authenticated.
        Assign a random staff member to the support request.
        """
        print("\n=== perform_create ===")
        print("Using serializer data:", serializer.validated_data)
        
        # Log the request data being used for creation
        print("\n=== Request Data ===")
        print("Request data:", self.request.data)
        print("Request POST:", self.request.POST)
        print("Request FILES:", dict(self.request.FILES) if hasattr(self.request, 'FILES') else 'No files')
        
        # Get or assign a staff member
        assigned_to = self.get_random_staff_member()
        if assigned_to:
            print(f"\n=== Assigning to Staff ===")
            print(f"Assigned to: {assigned_to.get_full_name() or assigned_to.username} (ID: {assigned_to.id})")
            # Set assigned_to in both context and validated_data
            serializer._validated_data['assigned_to'] = assigned_to
            serializer._context['assigned_to'] = assigned_to
            
            # Also set it in the request data to ensure it's included in the response
            if hasattr(self.request, 'data') and isinstance(self.request.data, dict):
                self.request.data._mutable = True
                self.request.data['assigned_to'] = assigned_to.id
                self.request.data._mutable = False
        else:
            print("\n=== WARNING: No active staff members found to assign ticket ===")
        
        # Set created_by if user is authenticated
        if self.request.user.is_authenticated and not self.request.user.is_anonymous:
            serializer._validated_data['created_by'] = self.request.user
            serializer._context['created_by'] = self.request.user
            print(f"Created by: {self.request.user.username} (ID: {self.request.user.id})")
        else:
            print("Created by: Anonymous user")
        
        # Handle contact field - map to email/phone
        contact = self.request.data.get('contact', '').strip()
        if contact:
            if '@' in contact:
                serializer.validated_data['email'] = contact
                if 'phone' not in serializer.validated_data:
                    serializer.validated_data['phone'] = ''
            else:
                phone = ''.join(c for c in contact if c.isdigit())
                if phone and len(phone) >= 10:
                    serializer.validated_data['phone'] = phone
                    if 'email' not in serializer.validated_data:
                        serializer.validated_data['email'] = f"no-email-{phone}@example.com"
        
        # Ensure required fields are present
        if 'name' not in serializer.validated_data:
            serializer.validated_data['name'] = self.request.data.get('name', 'Anonymous')
        
        if 'subject' not in serializer.validated_data:
            serializer.validated_data['subject'] = self.request.data.get('subject', 'No Subject')
        
        if 'message' not in serializer.validated_data:
            serializer.validated_data['message'] = self.request.data.get('message', 'No message provided')
        
        # Set default status if not provided
        if 'status' not in serializer.validated_data:
            serializer.validated_data['status'] = 'open'
        
        print("\n=== Final Validated Data ===")
        print(serializer.validated_data)
        
        # Save the instance
        instance = serializer.save()
        
        # Verify the saved data
        print("\n=== After Save ===")
        print(f"Instance ID: {instance.id}")
        print(f"Subject: {instance.subject}")
        print(f"Email: {getattr(instance, 'email', 'N/A')}")
        print(f"Phone: {getattr(instance, 'phone', 'N/A')}")
        print(f"Status: {instance.status}")
        print(f"Assigned to: {instance.assigned_to}")
        print(f"Created by: {instance.created_by}")
        
        # Log the full instance data for debugging
        print("\n=== Full Instance Data ===")
        for field in instance._meta.fields:
            print(f"{field.name}: {getattr(instance, field.name, 'N/A')}")

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