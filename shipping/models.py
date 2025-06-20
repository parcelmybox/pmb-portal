import re
import logging
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .constants import BILL_STATUS_CHOICES

User = get_user_model()

# Status and choice constants
PAYMENT_METHODS = [
    ('', ''),  # Empty default
    ('CASH', 'Cash'),
    ('CREDIT_CARD', 'Credit Card'),
    ('DEBIT_CARD', 'Debit Card'),
    ('BANK_TRANSFER', 'Bank Transfer'),
    ('GOOGLE_PAY', 'Google Pay'),
    ('ZELLE', 'Zelle'),
    ('OTHER', 'Other'),
]

COURIER_SERVICES = [
    ('', '-- Select Courier --'),
    ('DHL', 'DHL'),
    ('UPS', 'UPS'),
    ('FEDEX', 'FedEx'),
    ('USPS', 'USPS'),
    ('OTHER', 'Other'),
]

SHIPPING_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

# Package type choices
PACKAGE_TYPE_CHOICES = [
    ('box', 'Box'),
    ('envelope', 'Envelope'),
    ('tube', 'Tube'),
    ('pallet', 'Pallet'),
    ('other', 'Other'),
]

class CityCode(models.Model):
    """Model for storing city postal codes and locations."""
    city = models.CharField(max_length=100, verbose_name='City')
    state = models.CharField(max_length=100, verbose_name='State/Province')
    country = models.CharField(max_length=100, verbose_name='Country')
    postal_code = models.CharField(max_length=20, verbose_name='Postal Code')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'City Code'
        verbose_name_plural = 'City Codes'
        unique_together = ['city', 'state', 'country', 'postal_code']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['state']),
            models.Index(fields=['country']),
            models.Index(fields=['postal_code']),
        ]

    def __str__(self):
        return f"{self.city}, {self.state} {self.postal_code} ({self.country})"

    def save(self, *args, **kwargs):
        """Ensure postal code is always uppercase."""
        self.postal_code = self.postal_code.upper()
        super().save(*args, **kwargs)

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
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    address_line1 = models.CharField(max_length=255, verbose_name='Address Line 1')
    address_line2 = models.CharField(max_length=255, blank=True, verbose_name='Address Line 2 (Optional)')
    city = models.CharField(max_length=100, verbose_name='City')
    state = models.CharField(max_length=100, verbose_name='State/Province')
    country = models.CharField(max_length=100, verbose_name='Country')
    postal_code = models.CharField(max_length=20, verbose_name='Postal/Zip Code')
    phone_number = models.CharField(max_length=20, verbose_name='Phone Number')
    is_default = models.BooleanField(default=False, help_text='Set as default shipping address')

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.address_line1}, {self.city}, {self.state} {self.postal_code}"
    
    def clean(self):
        """Ensure only one default address per user"""
        if self.is_default and self.user_id:
            ShippingAddress.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class Invoice(models.Model):
    """Model for managing customer invoices."""
    
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
    shipment = models.OneToOneField(
        'Shipment', 
        on_delete=models.SET_NULL, 
        related_name='invoice',
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
        choices=(
            ('draft', 'Draft'),
            ('sent', 'Sent'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('cancelled', 'Cancelled'),
        ), 
        default='draft',
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
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        return f'Invoice #{self.id} - {self.customer.get_username()} - ${self.amount:.2f}'
    
    @property
    def is_paid(self):
        return self.status == 'PAID'
    
    @property
    def is_overdue(self):
        if self.status == 'PAID' or not self.due_date:
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
        if self.status != 'PAID':
            self.status = 'PAID'
            self.payment_method = payment_method
            self.paid_at = timezone.now()
            if commit:
                self.save(update_fields=['status', 'paid_at', 'payment_method', 'updated_at'])
            return True
        return False


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
    
    def generate_invoice(self, created_by=None, request=None):
        """Generate an invoice for this shipment.
        
        Args:
            created_by: User who is creating the invoice. Defaults to the shipment's sender.
            request: Optional request object to capture additional context
            
        Returns:
            Invoice: The created invoice instance
        """
        if not self.sender_address or not self.sender_address.user:
            raise ValueError("Cannot generate invoice: Shipment has no associated sender user")
            
        if not self.shipping_cost:
            raise ValueError("Cannot generate invoice: Shipping cost is not set")
        
        # Check if invoice already exists
        if hasattr(self, 'invoice') and self.invoice:
            return self.invoice
            
        # Get the customer from the sender's address or fall back to the created_by user
        customer = self.sender_address.user if self.sender_address and self.sender_address.user else created_by
        
        # If we still don't have a customer, use the created_by user
        if not customer and created_by:
            customer = created_by
            
        if not customer:
            raise ValueError("Cannot generate invoice: No customer or sender user available")
            
        # Calculate tax amount if applicable
        tax_rate = 0  # Default tax rate, you can modify this as needed
        tax_amount = (self.shipping_cost * tax_rate) / 100
        total_amount = self.shipping_cost + tax_amount
        
        invoice = Invoice.objects.create(
            customer=customer,
            amount=self.shipping_cost,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total_amount=total_amount,
            shipment=self,
            status='SENT',
            payment_method='CASH',
            created_by=created_by or customer,
            description=f"Shipping charge for {self.tracking_number}",
            due_date=timezone.now().date() + timezone.timedelta(days=15)  # 15-day payment term
        )
        
        # Log activity
        ActivityHistory.log_activity(
            user=created_by or self.sender_address.user,
            action='Invoice Generated from Shipment',
            obj=invoice,
            request=request
        )
        
        return invoice
        
    # Keep generate_bill for backward compatibility
    def generate_bill(self, *args, **kwargs):
        return self.generate_invoice(*args, **kwargs)

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
        return f"{self.get_status_display()} at {self.location} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class Bill(models.Model):
    """Model for managing customer bills and invoices."""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_bills')
    shipment = models.ForeignKey(
        'Shipment', 
        on_delete=models.SET_NULL, 
        related_name='bills',
        null=True,
        blank=True,
        help_text='Related shipment if this bill is for shipping charges'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[])
    status = models.CharField(max_length=10, choices=BILL_STATUS_CHOICES, default='PENDING')
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='CASH',
        verbose_name='Payment Method',
        help_text='Select the payment method used for this bill.'
    )
    package = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Package',
        help_text='Package type or description'
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Weight (kg)',
        help_text='Weight of the package in kilograms'
    )
    courier_service = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=COURIER_SERVICES,
        verbose_name='Courier Service',
        help_text='Select the courier service used for this shipment'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        return f'Bill #{self.id} - {self.customer.get_username()} - ${self.amount:.2f}'
    
    @property
    def is_paid(self):
        return self.status == 'PAID'
    
    @property
    def is_overdue(self):
        if self.status == 'PAID' or not self.due_date:
            return False
        return timezone.now().date() > self.due_date
    
    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days
    
    @property
    def days_until_due(self):
        if not self.due_date or self.status == 'PAID':
            return 0
        return (self.due_date - timezone.now().date()).days
    
    def mark_as_paid(self, commit=True):
        if self.status != 'PAID':
            self.status = 'PAID'
            self.paid_at = timezone.now()
            if commit:
                self.save(update_fields=['status', 'paid_at', 'updated_at'])
            return True
        return False
    
    def update_status(self, new_status=None):
        """Update the bill status and trigger related actions."""
        if new_status and new_status != self.status and new_status in dict(BILL_STATUS_CHOICES):
            self.status = new_status
            if new_status == 'PAID' and not self.paid_at:
                self.paid_at = timezone.now()
            self.save(update_fields=['status', 'paid_at', 'updated_at'])
            return True
            
        # If no new_status provided, update based on due date
        if self.status == 'PAID':
            return False
            
        if self.is_overdue and self.status != 'OVERDUE':
            self.status = 'OVERDUE'
            self.save(update_fields=['status', 'updated_at'])
            return True
        elif not self.is_overdue and self.status == 'OVERDUE':
            self.status = 'PENDING'
            self.save(update_fields=['status', 'updated_at'])
            return True
            
        return False

## Yuvaraj will cerate new model for pickup request table 

