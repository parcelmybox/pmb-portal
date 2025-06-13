from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from .constants import BILL_STATUS_CHOICES

User = get_user_model()

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

class Bill(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_bills')
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
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Bill #{self.id} - {self.customer.get_full_name() or self.customer.username} - ${self.amount:.2f}'
    
    def is_overdue(self):
        if self.status == 'PAID' or self.status == 'CANCELLED':
            return False
        if not self.due_date:
            return False
        return timezone.now().date() > self.due_date
    
    def mark_as_paid(self):
        self.status = 'PAID'
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at', 'updated_at'])
    
    def mark_as_overdue(self):
        if self.status not in ['PAID', 'CANCELLED']:
            self.status = 'OVERDUE'
            self.save(update_fields=['status', 'updated_at'])
    
    def update_status(self, new_status):
        if new_status in dict(BILL_STATUS_CHOICES).keys():
            self.status = new_status
            if new_status == 'PAID' and not self.paid_at:
                self.paid_at = timezone.now()
                self.save(update_fields=['status', 'paid_at', 'updated_at'])
            else:
                self.save(update_fields=['status', 'updated_at'])
            return True
        return False

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"Bill #{self.id} - {self.customer.get_username()} - {self.amount}"

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

    def update_status(self):
        if self.status == 'PAID':
            return
            
        if self.is_overdue and self.status != 'OVERDUE':
            self.status = 'OVERDUE'
            self.save(update_fields=['status', 'updated_at'])
        elif not self.is_overdue and self.status == 'OVERDUE':
            self.status = 'PENDING'
            self.save(update_fields=['status', 'updated_at'])
