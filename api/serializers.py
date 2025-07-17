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
    # Map frontend field names to model field names
    contact = serializers.CharField(
        write_only=True, 
        required=True,
        help_text="Mobile number or email address"
    )
    
    # This field is used for input only (write)
    category = serializers.ChoiceField(
        write_only=True, 
        required=False,
        source='request_type',  # Map to the request_type field in the model
        choices=[
            ('general', 'General'),
            ('price', 'Price'),
            ('tracking', 'Tracking'),
            ('documentation', 'Documentation'),
            ('pickup', 'Pickup'),
            ('other', 'Other')
        ]
    )
    
    # This field is used for output only (read)
    request_type = serializers.SerializerMethodField(read_only=True)
    
    def get_request_type(self, obj):
        return obj.request_type
    
    # Make email optional in the serializer as we'll handle it from contact field
    email = serializers.EmailField(required=False, write_only=True)
    assigned_to = serializers.SerializerMethodField(read_only=True)
    
    def get_assigned_to(self, obj):
        if obj.assigned_to:
            return {
                'id': obj.assigned_to.id,
                'username': obj.assigned_to.username,
                'email': obj.assigned_to.email,
                'full_name': f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
            }
        return None
        
    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)
        
        # Ensure request_type is included in the response
        if 'request_type' not in representation and hasattr(instance, 'request_type'):
            representation['request_type'] = instance.request_type
        
        # Add debug information
        if hasattr(instance, 'assigned_to') and instance.assigned_to:
            print(f"\n=== Serializer Debug ===")
            print(f"Instance ID: {instance.id}")
            print(f"Assigned to: {instance.assigned_to} (ID: {instance.assigned_to.id})")
            print(f"Assigned to in representation: {representation.get('assigned_to')}")
        
        return representation
    
    class Meta:
        model = SupportRequest
        fields = [
            'id',
            'ticket_number',
            'subject',
            'name',
            'email',
            'phone',
            'contact',  # Frontend field that maps to phone
            'request_type',
            'category',  # Frontend field that maps to request_type
            'message',
            'attachment',
            'status',
            'created_at',
            'updated_at',
            'resolved_at',
            'resolution_notes',
            'assigned_to',  # This will use the get_assigned_to method
            'created_by',
            'shipment'
        ]
        read_only_fields = [
            'id', 
            'ticket_number', 
            'created_at', 
            'updated_at',
            'resolved_at',
            'assigned_to',
            'created_by',
            'status'
        ]
    
    def validate(self, data):
        """
        Custom validation to handle field mappings and required fields
        """
        contact = data.pop('contact', '').strip()
        
        # Check if contact is email or phone
        if '@' in contact:
            data['email'] = contact
        else:
            # Remove any non-digit characters from phone number
            phone = ''.join(c for c in contact if c.isdigit())
            if not phone:
                raise serializers.ValidationError({
                    'contact': 'Please enter a valid mobile number or email address.'
                })
            data['phone'] = phone
            
        # Map category to request_type if request_type not provided
        if 'category' in data:
            data['request_type'] = data.pop('category')
            
        # Ensure required fields are present
        required_fields = ['name', 'subject', 'message']
        for field in required_fields:
            if field not in data or not data[field]:
                raise serializers.ValidationError({field: "This field is required."})
        
        # Set default values
        data.setdefault('status', 'open')
        data.setdefault('email', 'no-email@example.com' if not data.get('email') else data['email'])
        
        # Only set default request_type if it's not already set
        if 'request_type' not in data:
            data['request_type'] = 'general'
        
        return data
    
    def create(self, validated_data):
        """
        Create and return a new SupportRequest instance, given the validated data.
        """
        # Generate a unique ticket number if not provided
        if not validated_data.get('ticket_number'):
            import uuid
            validated_data['ticket_number'] = f"SR-{uuid.uuid4().hex[:8].upper()}"
            
        return super().create(validated_data)

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
    """
    Serializer for calculating shipping quotes.
    Validates and processes shipping quote requests.
    """
    shipping_route = serializers.ChoiceField(
        choices=["india-to-usa", "usa-to-india"],
        help_text="Shipping route (e.g., 'india-to-usa' or 'usa-to-india')"
    )
    type = serializers.ChoiceField(
        choices=["document", "package"],
        help_text="Type of shipment ('document' or 'package')"
    )
    origin = serializers.ChoiceField(
        choices=[
            "mumbai", "delhi", "bangalore", "chennai", "hyderabad",
            "new-york", "los-angeles", "chicago", "houston", "atlanta"
        ],
        help_text="Origin city"
    )
    destination = serializers.ChoiceField(
        choices=[
            "mumbai", "delhi", "bangalore", "chennai", "hyderabad",
            "new-york", "los-angeles", "chicago", "houston", "atlanta"
        ],
        help_text="Destination city"
    )
    weight = serializers.FloatField(
        min_value=0.1,
        help_text="Weight of the package"
    )
    weight_metric = serializers.ChoiceField(
        choices=["kg", "lb"],
        default="kg",
        help_text="Weight unit ('kg' or 'lb')"
    )
    dim_length = serializers.FloatField(
        min_value=1,
        help_text="Length dimension in cm"
    )
    dim_width = serializers.FloatField(
        min_value=1,
        help_text="Width dimension in cm"
    )
    dim_height = serializers.FloatField(
        min_value=1,
        help_text="Height dimension in cm"
    )
    usd_rate = serializers.FloatField(
        min_value=0.01,
        help_text="Current USD to INR exchange rate"
    )

    def validate(self, data):
        """
        Validate that origin and destination are valid for the selected route.
        """
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
                f"Valid origins: {', '.join(valid_origins)}"
            )

        if destination not in valid_destinations:
            errors["destination"] = (
                f"'{destination}' is not valid for route '{route}'. "
                f"Valid destinations: {', '.join(valid_destinations)}"
            )

        if errors:
            raise serializers.ValidationError(errors)

        return data