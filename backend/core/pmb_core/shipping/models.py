from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

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


class Bill(models.Model):
    BILL_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=BILL_STATUS_CHOICES, default='PENDING')
    due_date = models.DateField(null=True, blank=True, help_text="Due date for this bill")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"Bill {self.id} - {self.customer.get_full_name() or self.customer.username} - ${self.amount}"
    
    def mark_as_paid(self, commit=True):
        """Mark this bill as paid."""
        if self.status != 'PAID':
            self.status = 'PAID'
            if commit:
                self.save()
            return True
        return False
    
    def is_overdue(self):
        """Check if the bill is overdue."""
        if self.status == 'PAID' or not self.due_date:
            return False
        return timezone.now().date() > self.due_date
    
    def update_status(self):
        """Update the status based on due date and current status."""
        if self.status != 'PAID' and self.is_overdue():
            self.status = 'OVERDUE'
            self.save()
            return 'OVERDUE'
        return self.status
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('shipping:bill_detail', args=[str(self.id)])
    
    def save(self, *args, **kwargs):
        # Update status based on due date when saving
        if self.due_date and self.status != 'PAID':
            if self.is_overdue():
                self.status = 'OVERDUE'
        super().save(*args, **kwargs)


class ActivityHistory(models.Model):
    ACTIVITY_TYPES = [
        ('BILL_GENERATED', 'Bill Generated'),
        ('BILL_PAID', 'Bill Paid'),
        ('STATUS_CHANGED', 'Status Changed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reference_id = models.PositiveIntegerField(null=True, blank=True)
    reference_model = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Activity Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.user.username} - {self.created_at}"
