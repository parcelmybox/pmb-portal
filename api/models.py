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

class SupportRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('closed', 'Closed'),
    ]
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255)
    category = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='new')
    
    def __str__(self):
        return f"Support #{self.id} - {self.subject}"

class ShippingRates(models.Model):
    courier = models.CharField(max_length=50, null=True, blank=True)
    min_kg = models.DecimalField(max_digits=5, decimal_places=2)
    max_kg = models.DecimalField(max_digits=5, decimal_places=2)
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    per_kg_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    package_type = models.CharField(max_length=20, default='package')

    def __str__(self):
        return f"{self.courier} ({self.min_kg}-{self.max_kg}kg): {self.fixed_price if self.per_kg_price is None else self.per_kg_price}"

class Product(models.Model):
    name = models.CharField(max_length=150, unique=True, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    discounted_price = models.FloatField(blank=True, null=True)
    description = models.CharField(max_length=400, blank=True, null=True)
    tag = models.CharField(max_length=25, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.discounted_price}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f"Image for {self.product.name} - {self.image_url}"

class ProductWeights(models.Model):
    product = models.ForeignKey(Product, related_name='weights', on_delete=models.CASCADE, blank=True, null=True)
    weights = models.CharField(max_length=20)
    price = models.FloatField(null=True, blank=True)
    discounted_price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Weight for {self.product.name} - {self.weights} - {self.discounted_price}"