# Billing status choices
BILL_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('PAID', 'Paid'),
    ('OVERDUE', 'Unpaid'),  # Changed from 'Overdue' to 'Unpaid'
    ('CANCELLED', 'Cancelled'),
]

# Invoice status choices
INVOICE_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('paid', 'Paid'),
    ('overdue', 'Overdue'),
    ('cancelled', 'Cancelled'),
]

# Payment method choices
PAYMENT_METHODS = [
    ('credit_card', 'Credit Card'),
    ('paypal', 'PayPal'),
    ('bank_transfer', 'Bank Transfer'),
    ('cash', 'Cash'),
    ('check', 'Check'),
    ('other', 'Other'),
]
