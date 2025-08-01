from rest_framework import serializers
from django.contrib.auth import get_user_model
from shipping.models import (
    Shipment, ShippingAddress, Bill, Invoice, 
    ShipmentItem, TrackingEvent, Contact, SupportRequest
)
from django.utils import timezone
from api.models import Product, ProductImage, ProductWeights
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
            'status', 'shipping_date', 'delivery_date',
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


class SupportRequestListSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for listing support requests with better formatting.
    Groups related fields and provides human-readable values.
    """
    # Basic information
    ticket_info = serializers.SerializerMethodField()
    
    # Contact information
    contact_info = serializers.SerializerMethodField()
    
    # Status information
    status_info = serializers.SerializerMethodField()
    
    # Dates
    dates = serializers.SerializerMethodField()
    
    class Meta:
        model = SupportRequest
        fields = [
            'ticket_info',
            'subject',
            'contact_info',
            'status_info',
            'dates'
        ]
    
    def get_ticket_info(self, obj):
        """
        Group ticket-related information.
        """
        return {
            'id'           : obj.id,
            'ticket_number': obj.ticket_number,
            'category'     : obj.get_request_type_display(),
            'category_key' : obj.request_type
        }
    
    def get_contact_info(self, obj):
        """
        Group contact-related information.
        """
        is_placeholder_email = (
            obj.email == f'no-email-{obj.phone}@example.com' or 
            obj.email == 'no-email@example.com'
        )
        
        return {
            'name' : obj.name,
            'email': None if is_placeholder_email else obj.email,
            'phone': obj.phone if obj.phone and obj.phone.strip() else None
        }
    
    def get_status_info(self, obj):
        """
        Group status-related information.
        """
        has_resolution_notes = hasattr(obj, 'resolution_notes')
        is_closed = obj.status == 'closed'
        
        return {
            'status'         : obj.get_status_display(),
            'status_key'     : obj.status,
            'is_resolved'    : is_closed,
            'resolution_notes': obj.resolution_notes if has_resolution_notes and is_closed else None
        }
    
    def get_dates(self, obj):
        """
        Group date-related information.
        """
        return {
            'created' : obj.created_at,
            'updated' : obj.updated_at,
            'resolved': obj.resolved_at
        }


class SupportRequestSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the SupportRequest model.
    Used for create, retrieve, and update operations.
    """
    # Map frontend field names to model field names
    contact = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Mobile number or email address"
    )
    
    # Map category to request_type
    category = serializers.ChoiceField(
        write_only=True,
        required=False,
        choices=[
            ('general', 'General'),
            ('price', 'Price'),
            ('tracking', 'Tracking'),
            ('documentation', 'Documentation'),
            ('pickup', 'Pickup'),
            ('other', 'Other')
        ],
        default='general',
        help_text="Category of the support request"
    )
    
    # Add read-only fields for display
    ticket_number = serializers.CharField(read_only=True)
    request_type = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    resolved_at = serializers.DateTimeField(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(is_staff=True, is_active=True),
        required=False,
        allow_null=True
    )
    category_display = serializers.CharField(source='get_request_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SupportRequest
        fields = [
            'id',
            'ticket_number',
            'subject',
            'name',
            'email',
            'phone',
            'contact',  # Frontend field that maps to email/phone
            'category',  # Maps to request_type
            'request_type',
            'category_display',
            'message',
            'attachment',
            'status',
            'status_display',
            'created_at',
            'updated_at',
            'resolved_at',
            'resolution_notes',
            'assigned_to',
            'created_by',
            'shipment'
        ]
        extra_kwargs = {
            'email': {'required': False},  # Make email not required in serializer
            'phone': {'required': False},  # Make phone not required in serializer
        }
        read_only_fields = [
            'id',
            'ticket_number',
            'status',
            'status_display',
            'created_at',
            'updated_at',
            'resolved_at',
            'assigned_to',
            'created_by',
            'shipment',
            'request_type',  # This is set via the category field
            'category_display'
        ]
    
    def validate(self, data):
        """
        Validate the support request data and handle field mappings.
        """
        print("\n=== Validating Data ===")
        print(f"Raw data: {data}")
        
        # Make a copy to avoid modifying the original
        validated_data = data.copy()
        
        # Handle contact field (email/phone)
        contact = str(validated_data.pop('contact', '')).strip()
        print(f"Processing contact: {contact}")
        
        if not contact:
            raise serializers.ValidationError({
                'contact': 'Contact information is required. Please provide an email address or phone number.'
            })
        
        # Handle email/phone from contact field
        if '@' in contact:
            validated_data['email'] = contact
            validated_data['phone'] = ''  # Clear phone if email is provided
            print(f"Set email: {contact}")
        else:
            # If no email provided, require phone
            phone = ''.join(c for c in contact if c.isdigit())
            if not phone or len(phone) < 10:
                raise serializers.ValidationError({
                    'contact': 'Please enter a valid phone number (at least 10 digits) or email address.'
                })
            validated_data['phone'] = phone
            validated_data['email'] = f"no-email-{phone}@example.com"  # Provide a dummy email to satisfy the model
            print(f"Set phone: {phone} and dummy email")
        
        # Set default subject if not provided
        if 'subject' not in validated_data or not validated_data['subject']:
            validated_data['subject'] = 'No Subject'
            
        # Set default message if not provided
        if 'message' not in validated_data or not validated_data['message']:
            validated_data['message'] = 'No message provided'
        
        # Map category to request_type if needed
        if 'category' in validated_data:
            category = validated_data.pop('category')
            if category not in dict(self.fields['category'].choices):
                raise serializers.ValidationError({
                    'category': f'Invalid category. Must be one of: {list(dict(self.fields["category"].choices).keys())}'
                })
            validated_data['request_type'] = category
            print(f"Mapped category '{category}' to request_type")
        
        # Ensure name is set
        if 'name' not in validated_data or not validated_data['name']:
            validated_data['name'] = 'Anonymous User'
        
        return validated_data
        
        # Ensure required fields are present
        required_fields = ['name', 'subject', 'message']
        for field in required_fields:
            value = validated_data.get(field, '')
            if not value or (isinstance(value, str) and not value.strip()):
                raise serializers.ValidationError({
                    field: f"This field is required and cannot be empty."
                })
            
            # Clean string fields
            if isinstance(value, str):
                validated_data[field] = value.strip()
        
        # Set default status if not provided
        validated_data.setdefault('status', 'open')
        
        print("=== Validation Successful ===")
        print(f"Validated data: {validated_data}")
        
        return validated_data
    
    def create(self, validated_data):
        """
        Create and return a new SupportRequest instance, given the validated data.
        """
        from django.utils import timezone
        import uuid
        
        print("\n=== Creating Support Request ===")
        print(f"Validated data: {validated_data}")
        
        # Generate ticket number
        ticket_number = f"SR-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        print(f"Generated ticket number: {ticket_number}")
        
        # Get or set default values
        name = validated_data.get('name', 'Anonymous User')
        email = validated_data.get('email', '')
        phone = validated_data.get('phone', '')
        subject = validated_data.get('subject', 'No Subject')
        message = validated_data.get('message', 'No message provided')
        request_type = validated_data.get('request_type', 'general')
        
        # Get assigned_to and created_by from validated_data or context
        assigned_to = validated_data.pop('assigned_to', None) or self.context.get('assigned_to')
        created_by_id = validated_data.pop('created_by_id', None) or self.context.get('created_by_id')
        
        print(f"Assigned to: {assigned_to}")
        print(f"Created by ID: {created_by_id}")
        
        # Create the support request with all required fields
        support_request = SupportRequest.objects.create(
            ticket_number=ticket_number,
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            request_type=request_type,
            status='open',
            assigned_to=assigned_to,
            created_by_id=created_by_id
        )
        
        # Handle file upload if present
        if 'attachment' in validated_data:
            support_request.attachment = validated_data['attachment']
            support_request.save()
        
        print(f"Created support request with ID: {support_request.id}")
        print(f"Ticket Number: {support_request.ticket_number}")
        print(f"Status: {support_request.status}")
        
        return support_request


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
        choices=["document", "package", "medicine"],
        help_text="Type of shipment ('document', 'package', or 'medicine')"
    )
    origin = serializers.ChoiceField(
        choices=[
            "mumbai", "delhi", "bangalore", "chennai", "hyderabad",
        ],
        help_text="Origin city",
        allow_blank=True
    )
    destination = serializers.ChoiceField(
        choices=[
            "mumbai", "delhi", "bangalore", "chennai", "hyderabad",
        ],
        help_text="Destination city",
        allow_blank=True
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
    include_dimensions = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Whether to include package dimensions in the quote"
    )
    dim_length = serializers.FloatField(
        min_value=0,
        required=False,
        help_text="Length dimension in cm"
    )
    dim_width = serializers.FloatField(
        min_value=0,
        required=False,
        help_text="Width dimension in cm"
    )
    dim_height = serializers.FloatField(
        min_value=0,
        required=False,
        help_text="Height dimension in cm"
    )
    usd_rate = serializers.FloatField(
        min_value=0.01,
        help_text="Current USD to INR exchange rate"
    )
    carrier_preference_type = serializers.ChoiceField(
        choices=["fastest", "cheapest", "choose-manually"],
        default="fastest",
        help_text="Preferred carrier selection method"
    )
    carrier_preference = serializers.ChoiceField(
        choices=["", "ups", "dhl", "fedex"],
        required=False,
        help_text="Specific carrier preference (if 'choose-manually' is selected)"
    )
    currency = serializers.ChoiceField(
        choices=['₹', '$'],
        default='₹',
        help_text="Preferred currency for the quote"
    )

    def validate(self, data):
        """
        Validate that origin and destination are valid for the selected route.
        """
        route = data.get("shipping_route")
        origin = data.get("origin")
        destination = data.get("destination")

        india_cities = ["mumbai", "delhi", "bangalore", "chennai", "hyderabad"]

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

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image_url']
        read_only_fields = fields

class ProductWeightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductWeights
        fields = ['weights', 'price', 'discounted_price']
        read_only_fields = fields

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    weights = ProductWeightsSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'category',
            'price',
            'discounted_price',
            'description',
            'tag',
            'stock',
            'images',
            'weights',
        ]
        read_only_fields = fields

    def validate(self, data):
        if data.get('discounted_price') and data.get('price'):
            if data['discounted_price'] > data['price']:
                raise serializers.ValidationError("Discounted price cannot be greater than the original price.")
        return data