from rest_framework import serializers
from django.contrib.auth import get_user_model
from shipping.models import (
    Shipment, ShippingAddress, Bill, Invoice, 
    ShipmentItem, TrackingEvent, Contact, SupportRequest
)
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'is_staff', 'is_active', 'date_joined', 'last_login']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create user with superuser and staff privileges
        user = User.objects.create_superuser(
            **validated_data,
            is_staff=True,
            is_superuser=True
        )
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
            'id', 'shipment', 'name', 'quantity', 'description', 
            'declared_value'
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
            'user',
            'subject',
            'message',
            'request_type',
            'status',
            'created_at',
            'updated_at',
            'attachment',
            'resolution_notes'
        ]
        read_only_fields = ['id', 'ticket_number', 'user', 'created_at', 'updated_at', 'status']

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
    type = serializers.ChoiceField(choices=["document", "package", "medicine"])
    origin = serializers.ChoiceField(choices=["mumbai", "delhi", "bangalore", "chennai", "hyderabad"], allow_blank=True)
    destination = serializers.ChoiceField(choices=["mumbai", "delhi", "bangalore", "chennai", "hyderabad"], allow_blank=True)
    weight = serializers.FloatField()
    weight_metric = serializers.ChoiceField(choices=["kg", "lbs"])
    include_dimensions = serializers.BooleanField()
    dim_length = serializers.FloatField()
    dim_width = serializers.FloatField()
    dim_height = serializers.FloatField()
    usd_rate = serializers.FloatField()
    carrier_preference_type = serializers.ChoiceField(choices=["fastest", "cheapest", "choose-manually"])
    carrier_preference = serializers.ChoiceField(choices=["", "ups", "dhl", "fedex"])
    currency = serializers.ChoiceField(choices=['₹', '$'])

    def validate(self, data):
        route = data.get("shipping_route")
        origin = data.get("origin")
        destination = data.get("destination")

        india_cities = ["mumbai", "delhi", "bangalore", "chennai", "hyderabad"]
        usa_cities = ["new-york", "los-angeles", "chicago", "houston", "atlanta"]

        errors = {}

        # validates origin and destination are in their respective countries
        if route == "india-to-usa":
            if origin not in india_cities:
                errors["origin"] = (
                    f"'{origin}' is not a valid origin for route '{route}'. "
                    f"Valid origins: {india_cities}"
                )

        elif route == "usa-to-india":
            if destination not in india_cities:
                errors["destination"] = (
                    f"'{destination}' is not a valid destination for route '{route}'. "
                    f"Valid destinations: {india_cities}"
                )

        else:
            raise serializers.ValidationError("Invalid shipping route.")

        # validate carrier preference
        preference_type = data.get("carrier_preference_type")
        preference = data.get("carrier_preference")

        if preference_type in ["fastest", "cheapest"] and preference != "":
            errors["carrier_preference"] = (
                "Must be empty when preference type is 'fastest' or 'cheapest'."
            )

        if preference_type == "choose-manually" and preference not in ["ups", "dhl", "fedex"]:
            errors["carrier_preference"] = (
                "Must be one of 'ups', 'dhl', or 'fedex' when preference type is 'choose-manually'."
            )

        # validate dimensions based on include_dimensions
        include_dimensions = data.get("include_dimensions")
        length = data.get("dim_length")
        width = data.get("dim_width")
        height = data.get("dim_height")

        if include_dimensions:
            if length <= 0:
                errors["dim_length"] = "Must be greater than 0 if dimensions are included."
            if width <= 0:
                errors["dim_width"] = "Must be greater than 0 if dimensions are included."
            if height <= 0:
                errors["dim_height"] = "Must be greater than 0 if dimensions are included."

        if errors:
            raise serializers.ValidationError(errors)

        return data
