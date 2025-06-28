from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import Invoice

class BulkActionForm(forms.Form):
    """Form for bulk actions on invoices."""
    ACTION_CHOICES = [
        ('', '---------'),
        ('delete', 'Delete selected invoices'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'bulk-action'})
    )
    invoices = forms.ModelMultipleChoiceField(
        queryset=Invoice.objects.none(),  # Start with empty queryset
        widget=forms.MultipleHiddenInput(),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set the queryset based on user permissions
        if user:
            queryset = Invoice.objects.all()
            if not user.is_staff:
                queryset = queryset.filter(customer=user)
            self.fields['invoices'].queryset = queryset

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        invoices = cleaned_data.get('invoices')
        
        if action and not invoices:
            raise ValidationError(_('Please select at least one invoice.'))
            
        return cleaned_data
