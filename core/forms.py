from django import forms
from .models import Customer, Product, Payment, Invoice

class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

class CustomerForm(BootstrapModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email or email.strip() == '':
            return None
        return email


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PaymentForm(BootstrapModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_method', 'transaction_id']
