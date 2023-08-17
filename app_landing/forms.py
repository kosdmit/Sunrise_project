from django import forms

from app_landing.models import Order


class OrderCreateForm(forms.ModelForm):
    phone_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': '+7                      '}),
    )

    class Meta:
        model = Order
        fields = ['phone_number', ]
