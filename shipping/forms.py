from django import forms
from .models import Shipment, ShippingAddress

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
        fields = ['address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code', 'phone_number', 'is_primary']
        widgets = {
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
