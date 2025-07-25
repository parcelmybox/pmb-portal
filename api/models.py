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

class Product(models.Model):
    name = models.CharField(max_length=150, unique=True, blank=False, null=False)
    category = models.CharField(max_length=100, blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    discounted_price = models.FloatField(blank=False, null=False)
    description = models.CharField(max_length=400)
    weight = models.CharField(max_length=50, blank=True)
    tag = models.CharField(max_length=25, blank=False, null=False)
    stock = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.discounted_price}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f"Image for {self.product.name} - {self.image_url}"