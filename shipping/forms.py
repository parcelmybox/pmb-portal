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
    from .models import PACKAGE_TYPE_CHOICES
    
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
    package_type = forms.ChoiceField(
        choices=[('', '-- Select Package Type --')] + list(PACKAGE_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )

    courier_service = forms.ChoiceField(
        choices=COURIER_SERVICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Courier Service'
    )

    class Meta:
        model = Shipment
        fields = [
            'sender_address', 'sender_first_name', 'sender_last_name',
            'recipient_address', 'recipient_first_name', 'recipient_last_name',
            'package_type', 'weight', 'length', 'width', 'height', 'shipping_date',
            'courier_service'
        ]
        widgets = {
            'sender_address': forms.Select(attrs={'class': 'form-select address-select', 'data-type': 'sender'}),
            'recipient_address': forms.Select(attrs={'class': 'form-select address-select', 'data-type': 'recipient'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.1', 'required': 'required'}),
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
    # Input for customer name (not a model field)
    customer_name = forms.CharField(
        label='Customer Name',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter customer name',
            'autocomplete': 'off',
        })
    )

    customer_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    payment_mode = forms.ChoiceField(
        label='Payment Method',
        choices=Bill.PAYMENT_CHOICES,
        initial='ZELLE',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width: 100%;',
        })
    )

    status = forms.ChoiceField(
        label='Payment Status',
        choices=Bill.STATUS_CHOICES,
        initial='PENDING',
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'width: 100%;',
        })
    )

    class Meta:
        model = Bill
        fields = [
            'customer_name',  # not in model, handled in clean()
            'phone_number',
            'weight',
            'billed_weight',
            'package_fee',
            'porter_charges',
            'other_charges',
            'status',
            'due_date',
            'payment_mode',
        ]
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number',
                'autocomplete': 'off'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Weight in kg'
            }),
            'billed_weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Billed weight (rounded kg)'
            }),
            'package_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Package fee ($)'
            }),
            'porter_charges': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Porter charges ($)'
            }),
            'other_charges': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Other charges ($)'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # User who is creating the bill
        super().__init__(*args, **kwargs)

        if not self.instance.pk and not self.data.get('status'):
            self.initial['status'] = 'PENDING'

        if self.instance.pk and self.instance.customer:
            customer_name = self.instance.customer.get_full_name() or self.instance.customer.username
            self.initial['customer_name'] = customer_name
            self.initial['customer_id'] = self.instance.customer_id

        if not self.instance.due_date and not self.data.get('due_date'):
            self.initial['due_date'] = timezone.now().date() + timedelta(days=10)

        for field_name, field in self.fields.items():
            if field_name != 'customer_name':
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'form-select'
                else:
                    field.widget.attrs['class'] = 'form-control'

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now().date():
            raise forms.ValidationError('Due date cannot be in the past.')
        return due_date

    def clean(self):
        cleaned_data = super().clean()

        customer_name = cleaned_data.get('customer_name', '').strip()
        if not customer_name:
            self.add_error('customer_name', 'Please enter a customer name.')
            return cleaned_data

        user = None

        # Try matching by full name
        if ' ' in customer_name:
            first_name, last_name = customer_name.split(' ', 1)
            user = User.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name
            ).first()

        # Try alternative matching
        if not user:
            user = User.objects.filter(
                Q(first_name__iexact=customer_name) |
                Q(username__iexact=customer_name.lower().replace(' ', '.'))
            ).first()

        # Create new user if none found
        if not user:
            from django.utils.crypto import get_random_string

            base_username = customer_name.lower().replace(' ', '.')[:20]
            username = base_username
            counter = 1

            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            email = f"{username}@customer.parcelmybox.com"
            random_password = get_random_string(12)
            first_name = customer_name.split(' ')[0]
            last_name = ' '.join(customer_name.split(' ')[1:]) if ' ' in customer_name else ''

            user = User.objects.create_user(
                username=username,
                email=email,
                password=random_password,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )

        # Attach customer and creator
        if hasattr(self, 'instance'):
            self.instance.customer = user
            if self.user:
                self.instance.created_by = self.user

        if self.data:
            self.data = self.data.copy()
            self.data['customer_id'] = str(user.id)

        cleaned_data['customer'] = user
        return cleaned_data


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
