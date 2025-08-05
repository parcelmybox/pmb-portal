from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Feedback, Order, PickupRequest
from shipping.models import Shipment, ShippingAddress  # Added ShippingAddress
from django.utils import timezone

User = get_user_model()

# ====================== USER SERIALIZERS ======================
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
        user = User.objects.create_superuser(
            **validated_data,
            is_staff=True,
            is_superuser=True
        )
        return user

# ====================== SHIPPING SERIALIZERS ======================
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

# ====================== PICKUP SERIALIZERS ======================
class PickupRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupRequest
        fields = '__all__'  # Change to include all fields
        extra_kwargs = {
            'tracking_number': {'required': False},
            'time': {'required': True},  # Ensure time is required
            'date': {'required': True}   # Ensure date is required
        }

    def create(self, validated_data):
        # Generate tracking number if not provided
        if not validated_data.get('tracking_number'):
            import uuid
            validated_data['tracking_number'] = f"PMB-{uuid.uuid4().hex[:8].upper()}"
        
        return super().create(validated_data)
# ====================== ORDER SERIALIZERS ======================
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer_name', 
            'created_at', 'updated_at', 'is_completed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'order_id': {'required': True}
        }

# ====================== FEEDBACK SERIALIZERS ======================
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            'id', 'order', 'rating', 'message', 'image',
            'contact_email', 'contact_phone', 'submitted_at'
        ]
        read_only_fields = ['id', 'submitted_at']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.order:
            representation['order_id'] = instance.order.order_id
        return representation

# ====================== QUOTE SERIALIZER ======================
class QuoteSerializer(serializers.Serializer):
    shipping_route = serializers.ChoiceField(choices=["india-to-usa", "usa-to-india"])
    type = serializers.ChoiceField(choices=["document", "package"])
    origin = serializers.ChoiceField(choices=[
        "mumbai", "delhi", "bangalore", "chennai", "hyderabad", 
        "new-york", "los-angeles", "chicago", "houston", "atlanta"
    ])
    destination = serializers.ChoiceField(choices=[
        "mumbai", "delhi", "bangalore", "chennai", "hyderabad", 
        "new-york", "los-angeles", "chicago", "houston", "atlanta"
    ])
    weight = serializers.FloatField(min_value=0.1)
    weight_metric = serializers.ChoiceField(choices=["kg", "lb"])
    dim_length = serializers.FloatField(min_value=1)
    dim_width = serializers.FloatField(min_value=1)
    dim_height = serializers.FloatField(min_value=1)
    usd_rate = serializers.FloatField(min_value=0)

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