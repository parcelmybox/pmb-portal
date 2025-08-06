from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class PickupRequest(models.Model):
    PACKAGE_TYPES = [
        ('doc', 'Documents'),
        ('Medicine', 'Medicine'),
        ('small', 'Small Package (<1kg)'),
        ('medium', 'Medium Package (1-5kg)'),
        ('large', 'Large Package (5-10kg)'),
        ('xl', 'Extra Large (>10kg)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, default='small')
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_number = models.CharField(
    max_length=50, 
    unique=True, 
    blank=True, 
    null=True,
    default=None  # Add this line to make it truly optional
)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pickup Request'
        verbose_name_plural = 'Pickup Requests'

    def __str__(self):
        return f"Pickup #{self.id} for {self.name}"

class Order(models.Model):
    ORDER_STATUS = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
    ]
    
    pickup_request = models.OneToOneField(PickupRequest, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.order_id}"

    def save(self, *args, **kwargs):
        if self.status == 'delivered' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '★ Poor'),
        (2, '★★ Fair'),
        (3, '★★★ Good'),
        (4, '★★★★ Very Good'),
        (5, '★★★★★ Excellent'),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    message = models.TextField()
    image = models.ImageField(upload_to='feedback_images/%Y/%m/%d/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'

    def __str__(self):
        return f"Feedback for Order #{self.order.order_id if self.order else 'N/A'}"
