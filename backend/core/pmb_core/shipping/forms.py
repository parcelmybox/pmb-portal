from django import forms
from .models import Address, Shipment

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'country', 'postal_code']
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['tracking_number', 'sender', 'recipient', 'status']
        widgets = {
            'tracking_number': forms.TextInput(attrs={'class': 'form-control'}),
            'sender': forms.Select(attrs={'class': 'form-control'}),
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
        }
