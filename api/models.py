from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PickupRequest(models.Model):
    PACKAGE_TYPES = [
        ('doc', 'Documents'),
        ('small', 'Small Package (<1kg)'),
        ('medium', 'Medium Package (1-5kg)'),
        ('large', 'Large Package (5-10kg)'),
        ('xl', 'Extra Large (>10kg)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Pickup for {self.name}"
    

class PackageDetail(models.Model):
    PACKAGING_STATUS = [
        ('boxed', 'Boxed'),
        ('loose', 'Loose'),
        ('fragile', 'Fragile'),
    ]

    # no longer a FK—just store whatever integer the front end sends
    pickup_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Arbitrary pickup‐request ID (no FK check)"
    )

    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Weight in kilograms (e.g. 2.50)"
    )
    dimensions = models.CharField(
        max_length=50,
        help_text="L×W×H and unit, e.g. '30x20x10cm'"
    )
    contents_description = models.TextField()
    packaging_status = models.CharField(
        max_length=10,
        choices=PACKAGING_STATUS
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Package {self.id} (pickup_id={self.pickup_id})"
    
"""
class PackageDetail(models.Model):
    PACKAGING_STATUS_CHOICES = [
        ('boxed',   'Boxed'),
        ('loose',   'Loose'),
        ('fragile', 'Fragile'),
    ]

    package_id       = models.AutoField(primary_key=True)
    pickup           = models.ForeignKey(
                          'PickupRequest',
                          on_delete=models.CASCADE,
                          related_name='packages'
                       )
    weight           = models.DecimalField(max_digits=6, decimal_places=2)
    dimensions       = models.CharField(
                          max_length=100,
                          help_text="Length x Width x Height in cm"
                       )
    contents_description = models.TextField()
    packaging_status = models.CharField(
                          max_length=10,
                          choices=PACKAGING_STATUS_CHOICES
                       )
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Package {self.package_id} for {self.pickup.name}"

"""
