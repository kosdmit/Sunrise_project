from django import forms
from django.utils.translation import gettext_lazy as _

from app_landing.models import Order


class OrderCreateForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': '+7                      '}),
        label=_('phone number') + ":",
    )

    customer_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label=_('name') + ":",
    )

    class Meta:
        model = Order
        fields = ['phone_number', 'customer_name']
