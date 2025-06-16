from datetime import timedelta

from django import forms
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Shipment, ShippingAddress, User, Invoice
from .models import Bill, PAYMENT_METHODS
from .constants import BILL_STATUS_CHOICES, INVOICE_STATUS_CHOICES
from .models import COURIER_SERVICES

class ShipmentForm(forms.ModelForm):
    sender_first_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sender First Name'})
    )
    sender_last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sender Last Name'})
    )
    recipient_first_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient First Name'})
    )
    recipient_last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipient Last Name'})
    )

    class Meta:
        model = Shipment
        fields = [
            'sender_address', 'sender_first_name', 'sender_last_name',
            'recipient_address', 'recipient_first_name', 'recipient_last_name',
            'package_type', 'weight', 'length', 'width', 'height', 'declared_value', 'shipping_date'
        ]
        widgets = {
            'sender_address': forms.Select(attrs={'class': 'form-select address-select', 'data-type': 'sender'}),
            'recipient_address': forms.Select(attrs={'class': 'form-select address-select', 'data-type': 'recipient'}),
            'package_type': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
            'declared_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'required': 'required'}),
            'shipping_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'required': 'required'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter addresses to only show the current user's addresses
        if self.user:
            self.fields['sender_address'].queryset = ShippingAddress.objects.filter(user=self.user)
            self.fields['recipient_address'].queryset = ShippingAddress.objects.filter(user=self.user)
            
            # Set default sender address if user has one marked as default
            default_sender = ShippingAddress.objects.filter(user=self.user, is_default=True).first()
            if default_sender:
                self.fields['sender_address'].initial = default_sender
                self.initial['sender_first_name'] = default_sender.first_name
                self.initial['sender_last_name'] = default_sender.last_name
        
        # Set initial values for recipient name fields if recipient address is already selected
        if 'recipient_address' in self.initial and self.initial['recipient_address']:
            try:
                recipient = ShippingAddress.objects.get(id=self.initial['recipient_address'])
                self.initial['recipient_first_name'] = recipient.first_name
                self.initial['recipient_last_name'] = recipient.last_name
            except (ValueError, ShippingAddress.DoesNotExist):
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        sender_address = cleaned_data.get('sender_address')
        recipient_address = cleaned_data.get('recipient_address')
        
        # Ensure sender and recipient are different
        if sender_address and recipient_address and sender_address.id == recipient_address.id:
            raise forms.ValidationError('Sender and recipient addresses must be different.')
            
        # Ensure sender address belongs to the current user
        if self.user and sender_address and sender_address.user != self.user:
            raise forms.ValidationError('Invalid sender address.')
            
        # Ensure recipient address belongs to the current user
        if self.user and recipient_address and recipient_address.user != self.user:
            raise forms.ValidationError('Invalid recipient address.')
            
        return cleaned_data

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['first_name', 'last_name', 'address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code', 'phone_number', 'is_default']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
                'required': 'required'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
                'required': 'required'
            }),
            'address_line1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address, P.O. box, company name',
                'required': 'required'
            }),
            'address_line2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartment, suite, unit, building, floor, etc.'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City',
                'required': 'required'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province/Region',
                'required': 'required'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country',
                'required': 'required'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP/Postal code',
                'required': 'required'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. +1 234 567 8900',
                'required': 'required',
                'pattern': '^\+?[\d\s-]+$',
                'title': 'Enter a valid phone number with country code (e.g., +1 234 567 8900)'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_is_default'
            }),
        }
        error_messages = {
            'address_line1': {
                'required': 'Please enter the street address',
            },
            'city': {
                'required': 'Please enter the city',
            },
            'country': {
                'required': 'Please enter the country',
            },
            'postal_code': {
                'required': 'Please enter the postal code',
            },
            'phone_number': {
                'required': 'Please enter a phone number',
            },
        }
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Remove all non-digit characters except leading +
        cleaned_number = ''.join(c for c in str(phone_number) if c.isdigit() or c == '+')
        # Basic validation - at least 8 digits
        if sum(c.isdigit() for c in cleaned_number) < 8:
            raise forms.ValidationError('Please enter a valid phone number with area code')
        return cleaned_number
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        # If this is being set as default, unset any existing default addresses for this user
        if cleaned_data.get('is_default') and self.user:
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance


class BillForm(forms.ModelForm):
    # Simple text input for customer name
    customer_name = forms.CharField(
        label='Customer Name',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter customer name',
            'autocomplete': 'off',
        })
    )
    
    # Hidden field to store the customer ID after creation
    customer_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    payment_method = forms.ChoiceField(
        label='Payment Method',
        choices=PAYMENT_METHODS,
        initial='GOOGLE_PAY',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width: 100%;',
        })
    )
    
    status = forms.ChoiceField(
        label='Payment Status',
        choices=BILL_STATUS_CHOICES,
        initial='PENDING',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width: 100%;',
        })
    )
    
    class Meta:
        model = Bill
        fields = ['customer_name', 'package', 'weight', 'courier_service', 'amount', 'status', 'description', 'payment_method']
        widgets = {
            'package': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter package type or description',
                'autocomplete': 'off'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Weight in kg'
            }),
            'courier_service': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter courier service name',
                'autocomplete': 'off'
            }),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter bill description (optional)'
            }),
        }
        help_texts = {
            'amount': 'Enter the total amount to be billed',
            'due_date': 'Date by which the payment is due',
            'description': 'Optional description or reference for this bill'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set choices for courier_service field
        self.fields['courier_service'].widget = forms.Select(choices=COURIER_SERVICES, attrs={'class': 'form-select'})
        
        # Ensure customer_name remains a simple text input
        self.fields['customer_name'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter customer name',
            'autocomplete': 'off',
            'data-select2-enable': 'false',
            'style': 'background-image: none !important;'
        })
        
        # Set default status for new bills if not already set
        if not self.instance.pk and not self.data.get('status'):
            self.initial['status'] = 'PENDING'
        
        # Set initial customer value if editing existing bill
        if self.instance.pk and self.instance.customer:
            customer_name = self.instance.customer.get_full_name() or self.instance.customer.username
            self.initial['customer_name'] = customer_name
            self.initial['customer_id'] = self.instance.customer_id
            
        # Set default due date to 10 days from now if not set
        if not self.instance.due_date and not self.data.get('due_date'):
            self.initial['due_date'] = timezone.now().date() + timedelta(days=10)
            
        # Set CSS classes for fields
        for field_name, field in self.fields.items():
            if field_name == 'status':
                field.widget.attrs['class'] = 'form-select'
            elif field_name != 'customer_name':  # Skip customer_name as it's already set
                field.widget.attrs['class'] = 'form-control'
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError('Due date cannot be in the past.')
        return due_date
        
    def clean(self):
        cleaned_data = super().clean()
        print("\n=== CLEAN METHOD ===")
        print(f"All cleaned_data: {cleaned_data}")
        
        # Get customer name from form
        customer_name = cleaned_data.get('customer_name', '').strip()
        if not customer_name:
            self.add_error('customer_name', 'Please enter a customer name.')
            return cleaned_data
        
        print(f"Processing customer: {customer_name}")
        
        # Try to find existing customer by name
        user = None
        
        # First, try to find by exact name match
        if ' ' in customer_name:
            first_name, last_name = customer_name.split(' ', 1)
            user = User.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name
            ).first()
        
        # If no match, try more flexible search
        if not user:
            user = User.objects.filter(
                Q(first_name__iexact=customer_name) |
                Q(username__iexact=customer_name.lower().replace(' ', '.'))
            ).first()
        
        # If still no user found, create a new one
        if not user:
            print(f"Creating new customer: {customer_name}")
            try:
                # Generate a unique username
                base_username = customer_name.lower().replace(' ', '.')[:20]
                username = base_username
                counter = 1
                
                # Ensure username is unique
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Create a temporary email
                email = f"{username}@customer.parcelmybox.com"
                
                # Generate a secure random password
                from django.utils.crypto import get_random_string
                random_password = get_random_string(12)
                
                # Create the new user
                first_name = customer_name.split(' ')[0]
                last_name = ' '.join(customer_name.split(' ')[1:]) if ' ' in customer_name else ''
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=random_password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True,
                    is_staff=False
                )
                
                print(f"Created new customer: {user} (ID: {user.id})")
                
            except Exception as e:
                error_msg = f"Error creating new customer: {str(e)}"
                print(error_msg)
                self.add_error('customer_name', error_msg)
                return cleaned_data
        
        # Set the customer on the instance
        if hasattr(self, 'instance'):
            self.instance.customer = user
            print(f"Set bill customer to: {user} (ID: {user.id})")
        
        # Store the customer ID in the form data
        if self.data:
            self.data = self.data.copy()
            self.data['customer_id'] = str(user.id)
        
        cleaned_data['customer'] = user
        print(f"Final cleaned_data: {cleaned_data}")
        return cleaned_data
    
    def clean_status(self):
        # Debug: Print initial status data
        print("\n=== CLEAN_STATUS ===")
        print(f"Initial cleaned_data: {self.cleaned_data}")
        print(f"Initial status: {self.cleaned_data.get('status')}")
        print(f"Instance exists: {hasattr(self, 'instance')}")
        if hasattr(self, 'instance'):
            print(f"Instance status: {getattr(self.instance, 'status', 'N/A')}")
        
        status = self.cleaned_data.get('status')
        print(f"Status from form: {status}")
        
        if not status and hasattr(self, 'instance'):
            print("Using instance status")
            return self.instance.status
            
        result = status or 'PENDING'
        print(f"Final status: {result}")
        return result


class InvoiceForm(forms.ModelForm):
    """Form for creating and updating invoices."""
    
    class Meta:
        model = Invoice
        fields = [
            'customer', 'shipment', 'amount', 'tax_rate', 'tax_amount', 
            'total_amount', 'status', 'due_date', 'payment_method', 
            'payment_date', 'transaction_id', 'notes'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'shipment': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': True}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = INVOICE_STATUS_CHOICES
        self.fields['payment_method'].choices = PAYMENT_METHODS
        
        # Set default due date to 30 days from now if not set
        if not self.instance.due_date:
            self.initial['due_date'] = timezone.now().date() + timezone.timedelta(days=30)
        
        # If this is a new invoice, set default status to 'draft'
        if not self.instance.pk:
            self.initial['status'] = 'draft'
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Calculate total amount if not set
        amount = cleaned_data.get('amount', 0) or 0
        tax_rate = cleaned_data.get('tax_rate', 0) or 0
        tax_amount = (amount * tax_rate) / 100
        
        # Update tax amount and total amount
        cleaned_data['tax_amount'] = tax_amount
        cleaned_data['total_amount'] = amount + tax_amount
        
        return cleaned_data


class BillFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'All Statuses'),
    ] + list(BILL_STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    customer = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control datepicker',
            'type': 'date'
        })
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by ID, customer, or description...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show customers if user is staff
        if user and user.is_staff:
            self.fields['customer'].queryset = User.objects.filter(
                Q(bills__isnull=False) | Q(is_staff=False)
            ).distinct().order_by('username')
        else:
            # Remove customer filter for non-staff
            del self.fields['customer']
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data
