from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()

class Invoice(models.Model):
    """Model for managing customer invoices."""
    
    # Status choices
    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_PAID = 'paid'
    STATUS_OVERDUE = 'overdue'
    STATUS_CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_SENT, 'Sent'),
        (STATUS_PAID, 'Paid'),
        (STATUS_OVERDUE, 'Overdue'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]
    
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='invoices',
        verbose_name='Customer'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_invoices',
        verbose_name='Created By'
    )
    shipment = models.ForeignKey(
        'Shipment', 
        on_delete=models.SET_NULL, 
        related_name='invoices',
        null=True,
        blank=True,
        help_text='Related shipment if this invoice is for shipping charges'
    )
    
    # Amount fields
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        verbose_name='Subtotal'
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=0,
        verbose_name='Tax Rate (%)',
        help_text='Tax rate as a percentage (e.g., 7.5 for 7.5%)'
    )
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        verbose_name='Tax Amount'
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        verbose_name='Total Amount',
        help_text='Subtotal + Tax Amount'
    )
    
    # Status and dates
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=STATUS_DRAFT,
        verbose_name='Status'
    )
    due_date = models.DateField(verbose_name='Due Date')
    payment_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Payment Date'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    
    # Payment information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='CASH',
        verbose_name='Payment Method',
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Transaction ID',
        help_text='Payment processor transaction ID'
    )
    
    # Additional information
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    notes = models.TextField(blank=True, null=True, verbose_name='Internal Notes')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['customer']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f'INV-{self.id:06d} - {self.customer.get_username()}'
    
    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID
    
    @property
    def is_overdue(self):
        if self.status in [self.STATUS_PAID, self.STATUS_CANCELLED] or not self.due_date:
            return False
        return timezone.now().date() > self.due_date
    
    def save(self, *args, **kwargs):
        # Calculate tax amount if not set
        if not self.tax_amount and self.tax_rate and self.amount:
            self.tax_amount = (self.amount * self.tax_rate) / 100
        
        # Calculate total amount
        self.total_amount = self.amount + self.tax_amount
        
        # Update the updated_at timestamp
        self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def mark_as_paid(self, payment_method='CASH', commit=True):
        if self.status != self.STATUS_PAID:
            self.status = self.STATUS_PAID
            self.payment_method = payment_method
            self.payment_date = timezone.now()
            if commit:
                self.save(update_fields=['status', 'payment_date', 'payment_method', 'updated_at'])
            return True
        return False
