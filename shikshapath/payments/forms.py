from django import forms
from .models import Payout


class PayoutForm(forms.ModelForm):
    """Form for creating payouts"""

    class Meta:
        model = Payout
        fields = ('bank_account', 'payment_method', 'notes')
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Account Info'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }
