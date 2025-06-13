from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

SHIPPING_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

PACKAGE_TYPE_CHOICES = [
    ('document', 'Documents'),
    ('parcel', 'Parcel'),
    ('oversized', 'Oversized'),
    ('liquid', 'Liquid'),
    ('fragile', 'Fragile'),
]

class Contact(models.Model):
    """Model to store contact information"""
    first_name = models.CharField(max_length=100, verbose_name='First Name', default='')
    last_name = models.CharField(max_length=100, verbose_name='Last Name', default='')
    email = models.EmailField(unique=True, validators=[EmailValidator()], verbose_name='Email', default='')
    phone_number = models.CharField(max_length=20, verbose_name='Phone Number', default='')
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name='Company')
    country = models.CharField(max_length=100, verbose_name='Country', default='USA')
    notes = models.TextField(blank=True, null=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    is_verified = models.BooleanField(default=False, verbose_name='Is Verified')

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        if not name:
            name = self.email or self.phone_number or 'Unnamed Contact'
        return name

    def clean(self):
        """Custom validation"""
        # Check required fields
        required_fields = {
            'first_name': 'First name is required',
            'last_name': 'Last name is required',
            'email': 'Email is required',
            'phone_number': 'Phone number is required',
            'country': 'Country is required'
        }
        
        for field, error_msg in required_fields.items():
            if not getattr(self, field, None):
                raise ValidationError({field: error_msg})
                
        # Clean and validate phone number if provided
        if self.phone_number:
            cleaned = re.sub(r'\D', '', self.phone_number)
            if len(cleaned) < 10:
                raise ValidationError('Phone number must be at least 10 digits')
            self.phone_number = cleaned

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        return self


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses', null=True, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False, help_text='Set as default shipping address')

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state} {self.postal_code}"
    
    def clean(self):
        """Ensure only one primary address per contact"""
        if self.is_primary and self.contact_id:
            ShippingAddress.objects.filter(
                contact=self.contact,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Shipment(models.Model):
    sender_address = models.ForeignKey(ShippingAddress, related_name='sender_shipments', on_delete=models.CASCADE)
    recipient_address = models.ForeignKey(ShippingAddress, related_name='recipient_shipments', on_delete=models.CASCADE)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES)
    weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    length = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    width = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    height = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    declared_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES, default='pending')
    tracking_number = models.CharField(max_length=50, unique=True)
    shipping_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment #{self.id} - {self.tracking_number}"

class ShipmentItem(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    description = models.TextField()
    declared_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.name} x{self.quantity}"

class TrackingEvent(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='tracking_events', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES)
    location = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.TextField()

    def __str__(self):
        return f"{self.get_status_display()} - {self.timestamp}"
