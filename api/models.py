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


# ✅ New SupportRequest model added here
class SupportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    attachment = models.FileField(upload_to='support_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
