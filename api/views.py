from django.shortcuts import render
from rest_framework import viewsets, status, filters, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.db import models
import math

from .models import User, PickupRequest, Feedback, Order
from .serializers import (
    UserSerializer,
    PickupRequestSerializer,
    FeedbackSerializer,
    OrderSerializer,
    ShipmentSerializer,
    ShippingAddressSerializer,
    QuoteSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly
from shipping.models import Shipment, ShippingAddress, Bill, Invoice, ShipmentItem, TrackingEvent, SupportRequest

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    - Admins can list and manage all users
    - Regular users can only view/update their own data
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['date_joined', 'username']
    ordering = ['-date_joined']

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class PickupRequestViewSet(viewsets.ModelViewSet):
    """
    Public API endpoint for pickup requests that:
    - Allows completely unauthenticated access for all actions
    - No user association required
    - Maintains all search/filter capabilities
    """
    queryset = PickupRequest.objects.all()
    serializer_class = PickupRequestSerializer
    permission_classes = [AllowAny]  # No authentication required for any action
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'email', 'phone_number', 'city', 'postal_code']
    ordering_fields = ['date', 'time', 'created_at']
    ordering = ['-created_at']

    # Remove all user-related logic since we don't need authentication
    def perform_create(self, serializer):
        """Simple save without any user association"""
        serializer.save()

    # Simplified get_queryset since we don't need user filtering
    def get_queryset(self):
        return super().get_queryset()

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Public endpoint for upcoming pickups"""
        queryset = self.filter_queryset(self.get_queryset())
        today = timezone.now().date()
        upcoming = queryset.filter(date__gte=today).order_by('date', 'time')
        
        page = self.paginate_queryset(upcoming)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Public rescheduling endpoint"""
        pickup = self.get_object()
        new_date = request.data.get('date')
        new_time = request.data.get('time')
        
        if not new_date or not new_time:
            return Response(
                {'error': 'Both date and time are required for rescheduling'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        pickup.date = new_date
        pickup.time = new_time
        pickup.save()
        
        return Response(
            {'status': 'Pickup rescheduled successfully'}, 
            status=status.HTTP_200_OK
        )
class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for feedback that allows:
    - Unauthenticated submissions
    - Admin users to view and manage all feedback
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_id', 'message']
    ordering_fields = ['submitted_at', 'rating']
    ordering = ['-submitted_at']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for orders that allows:
    - Unauthenticated creation (if needed for your workflow)
    - Admin users to view and manage all orders
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['order_id', 'customer_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        order = self.get_object()
        order.is_completed = True
        order.save()
        return Response({'status': 'Order marked as completed'}, status=status.HTTP_200_OK)


class QuoteView(APIView):
    """
    API endpoint for shipping quotes that allows unauthenticated access
    """
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = QuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipping_route = serializer.validated_data["shipping_route"]
        package_type = serializer.validated_data["type"]
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
        package_multiplier = 1.0 if package_type == "document" else 1.5
        inr_price = math.ceil(base_price * route_multiplier * package_multiplier)
        usd_price = math.ceil(inr_price / usd_rate)

        shipping_time = "10-15 business days" if shipping_route == "india-to-usa" else "7-10 business days"

        return Response({
            "inr_price": inr_price,
            "usd_price": usd_price,
            "chargeable_weight": chargeable_weight,
            "shipping_time": shipping_time,
            "currency": "INR",
            "estimated_delivery": shipping_time
        })
