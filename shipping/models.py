from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

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

class ShippingAddress(models.Model):
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.country}"

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
