from django.db import models
from django.utils import timezone

class Address(models.Model):
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"

class Shipment(models.Model):
    tracking_number = models.CharField(max_length=50, unique=True)
    sender = models.ForeignKey(Address, related_name='sent_shipments', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Address, related_name='received_shipments', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tracking_number

class ShippingRate(models.Model):
    weight_range_start = models.DecimalField(max_digits=10, decimal_places=2)
    weight_range_end = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"${self.price} for {self.weight_range_start}-{self.weight_range_end} kg"
