from datetime import timedelta

from django import forms
from django.utils import timezone
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .models import Shipment, ShippingAddress, User
from .bill_models import Bill, PAYMENT_METHODS
from .constants import BILL_STATUS_CHOICES

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['sender_address', 'recipient_address', 'package_type', 'weight', 'length', 'width', 'height', 'declared_value', 'shipping_date']
        widgets = {
            'sender_address': forms.Select(attrs={'class': 'form-select'}),
            'recipient_address': forms.Select(attrs={'class': 'form-select'}),
            'package_type': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'declared_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'shipping_date': forms.DateInput(attrs={'class': 'form-control datepicker'}),
        }

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code', 'phone_number']
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BillForm(forms.ModelForm):
    # Use CharField instead of ModelChoiceField for customer
    customer_input = forms.CharField(
        label='Customer',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter customer name or email',
            'style': 'width: 100%',
            'autocomplete': 'off'
        })
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
    
    class Meta:
        model = Bill
        fields = ['amount', 'status', 'due_date', 'description', 'payment_method']  # Added payment_method to fields
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control datepicker', 'type': 'date', 'min': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter bill description (optional)'}),
        }
        help_texts = {
            'amount': 'Enter the total amount to be billed',
            'due_date': 'Date by which the payment is due',
            'description': 'Optional description or reference for this bill'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        print("\n=== FORM INIT ===")
        print(f"Initial args: {args}")
        print(f"Initial kwargs: {kwargs}")
        print(f"Initial data: {kwargs.get('data')}")
        
        super().__init__(*args, **kwargs)
        
        print(f"After super() - initial: {self.initial}")
        print(f"Instance exists: {hasattr(self, 'instance')}")
        if hasattr(self, 'instance'):
            print(f"Instance status: {getattr(self.instance, 'status', 'N/A')}")
        
        # Set default status for new bills if not already set
        if not self.instance.pk and not self.data.get('status'):
            print("Setting default status to PENDING")
            self.initial['status'] = 'PENDING'
        
        print(f"After setting default status - initial: {self.initial}")
        
        # Set initial customer value if editing existing bill
        if self.instance.pk and self.instance.customer:
            customer_name = self.instance.customer.get_full_name() or self.instance.customer.username
            print(f"Setting initial customer: {customer_name}")
            self.initial['customer_input'] = customer_name
            
        # Set default due date to 10 days from now if not set
        if not self.instance.due_date and not self.data.get('due_date'):
            self.initial['due_date'] = timezone.now().date() + timedelta(days=10)
            
        print(f"Final initial data: {self.initial}")
            
        # Add CSS class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-select' if field_name == 'status' else 'form-control'
            print(f"Field {field_name} attrs: {field.widget.attrs}")
    
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
        
    def clean(self):
        cleaned_data = super().clean()
        print("\n=== CLEAN METHOD ===")
        print(f"Status after clean_status: {cleaned_data.get('status')}")
        print(f"All cleaned_data: {cleaned_data}")
        
        # Handle customer input
        customer_input = cleaned_data.get('customer_input', '').strip()
        if customer_input:
            # Try to find existing user by email, username, or name
            user = User.objects.filter(
                Q(email__iexact=customer_input) | 
                Q(username__iexact=customer_input) |
                Q(first_name__iexact=customer_input) |
                Q(last_name__iexact=customer_input) |
                Q(first_name__iexact=' '.join(customer_input.split()[:-1]), 
                  last_name__iexact=customer_input.split()[-1] if ' ' in customer_input else '')
            ).first()
            
            if user:
                print(f"Found user in clean(): {user.get_full_name()} (ID: {user.id})")
                self.instance.customer = user
            else:
                print(f"No user found for input: {customer_input}")
                if not self.instance.pk:  # Only raise error for new bills
                    self.add_error('customer_input', 'No matching user found. Please enter a valid customer name or email.')
        
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
