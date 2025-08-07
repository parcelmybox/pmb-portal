from rest_framework import serializers
from django.contrib.auth import get_user_model
from shipping.models import (
    Shipment, ShippingAddress, Bill, Invoice, 
    ShipmentItem, TrackingEvent, Contact, SupportRequest
)
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data['email']
        validated_data['username'] = email  # Set username = email

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone_number',
            'company', 'country', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'user', 'first_name', 'last_name', 'address_line1', 
            'address_line2', 'city', 'state', 'country', 'postal_code', 
            'phone_number', 'is_default'
        ]
        read_only_fields = ['id', 'user']

class ShipmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentItem
        fields = [
            'id', 'shipment','name', 'quantity', 'description'
        ]
        read_only_fields = ['id', 'created_at']

class TrackingEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackingEvent
        fields = [
            'id', 'shipment', 'status', 'location', 
            'description', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

class ShipmentSerializer(serializers.ModelSerializer):
    sender_address = ShippingAddressSerializer()
    recipient_address = ShippingAddressSerializer()
    items = ShipmentItemSerializer(many=True, read_only=True)
    tracking_events = TrackingEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'tracking_number', 'sender_address', 'recipient_address',
            'package_type', 'weight', 'length', 'width', 'height',
            'declared_value', 'status', 'shipping_date', 'delivery_date',
            'shipping_cost', 'created_at', 'updated_at', 'items', 'tracking_events'
        ]
        read_only_fields = [
            'id', 'tracking_number', 'status', 'shipping_cost', 
            'created_at', 'updated_at', 'items', 'tracking_events'
        ]

    def create(self, validated_data):
        sender_data = validated_data.pop('sender_address')
        recipient_data = validated_data.pop('recipient_address')
        
        # Create or update sender address
        sender_address = ShippingAddress.objects.create(
            user=self.context['request'].user,
            **sender_data
        )
        
        # Create recipient address
        recipient_address = ShippingAddress.objects.create(
            user=None,  # Recipient might be a different user or not a user at all
            **recipient_data
        )
        
        # Create the shipment
        shipment = Shipment.objects.create(
            sender_address=sender_address,
            recipient_address=recipient_address,
            **validated_data
        )
        
        return shipment

class BillSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Bill
        fields = [
            'id', 'customer', 'created_by', 'shipment', 'amount',
            'status', 'due_date', 'payment_method', 'paid_at',
            'package', 'weight', 'courier_service', 'created_at', 'updated_at',
            'description'
        ]
        read_only_fields = [
            'id', 'customer', 'created_by', 'created_at', 'updated_at', 'paid_at'
        ]

class InvoiceSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    shipment = serializers.PrimaryKeyRelatedField(
        queryset=Shipment.objects.all(), 
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'customer', 'created_by', 'shipment',
            'amount', 'tax_rate', 'tax_amount', 'total_amount', 'status',
            'due_date', 'payment_date', 'payment_method', 'transaction_id',
            'description', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer', 'created_by', 'tax_amount',
            'total_amount', 'payment_date', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        # Calculate tax_amount and total_amount if amount or tax_rate changes
        if 'amount' in data or 'tax_rate' in data:
            amount = data.get('amount', self.instance.amount if self.instance else 0)
            tax_rate = data.get('tax_rate', self.instance.tax_rate if self.instance else 0)
            tax_amount = (amount * tax_rate) / 100
            data['tax_amount'] = tax_amount
            data['total_amount'] = amount + tax_amount
        return data


from rest_framework import serializers
from .models import PickupRequest


class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = [
            'id',
            'ticket_number',
            #'user',
            'subject',
            'message',
            'request_type',
            'status',
            'created_at',
            'updated_at',
            'attachment',
            'resolution_notes'
        ]
        read_only_fields = ['id', 'ticket_number', 'created_at', 'updated_at', 'status']

class PickupRequestSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = PickupRequest
        fields = '__all__'
        read_only_fields = ('user', 'created_at')
        extra_kwargs = {
            # Allow partial updates for PATCH
            'name': {'required': False},
            'phone_number': {'required': False},
            'email': {'required': False},
            'address': {'required': False},
            'city': {'required': False},
            'postal_code': {'required': False},
            'date': {'required': False},
            'time': {'required': False},
            'package_type': {'required': False},
            'weight': {'required': False}
        }
class QuoteSerializer(serializers.Serializer):
    shipping_route = serializers.ChoiceField(choices=["india-to-usa", "usa-to-india"])
    type = serializers.ChoiceField(choices=["document", "package"])
    origin = serializers.ChoiceField(choices=["mumbai", "delhi", "bangalore", "chennai", "hyderabad", "new-york", "los-angeles", "chicago", "houston", "atlanta"])
    destination = serializers.ChoiceField(choices=["mumbai", "delhi", "bangalore", "chennai", "hyderabad", "new-york", "los-angeles", "chicago", "houston", "atlanta"])
    weight = serializers.FloatField()
    weight_metric = serializers.ChoiceField(choices=["kg", "lb"])
    dim_length = serializers.FloatField()
    dim_width = serializers.FloatField()
    dim_height = serializers.FloatField()
    usd_rate = serializers.FloatField()

    def validate(self, data):
        route = data.get("shipping_route")
        origin = data.get("origin")
        destination = data.get("destination")

        india_cities = ["mumbai", "delhi", "bangalore", "chennai", "hyderabad"]
        usa_cities = ["new-york", "los-angeles", "chicago", "houston", "atlanta"]

        if route == "india-to-usa":
            valid_origins = india_cities
            valid_destinations = usa_cities
        elif route == "usa-to-india":
            valid_origins = usa_cities
            valid_destinations = india_cities
        else:
            raise serializers.ValidationError("Invalid shipping route.")

        errors = {}

        if origin not in valid_origins:
            errors["origin"] = (
                f"'{origin}' is not valid for route '{route}'. "
                f"Valid origins: {valid_origins}"
            )

        if destination not in valid_destinations:
            errors["destination"] = (
                f"'{destination}' is not valid for route '{route}'. "
                f"Valid destinations: {valid_destinations}"
            )

        if errors:
            raise serializers.ValidationError(errors)

        return data
    
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth import get_user_model
import traceback

import traceback
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            email = attrs.get("email")
            password = attrs.get("password")

            print("DEBUG - Email:", email)
            print("DEBUG - Password:", password)

            if not email or not password:
                raise serializers.ValidationError("Email and password are required")

            user = User.objects.filter(email=email).first()
            print("DEBUG - Found user:", user)

            if not user or not user.check_password(password) or not user.is_active:
                raise serializers.ValidationError("Invalid credentials or inactive user")

            refresh = RefreshToken.for_user(user)

            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "email": user.email,
                "user_id": user.id,
                "first_name": user.first_name,
            }

        except Exception as e:
            print("EXCEPTION in validate():", str(e))
            traceback.print_exc()
            raise e
