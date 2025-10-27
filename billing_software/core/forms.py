from django import forms
from .models import Customer, Product
from .models import Invoice, InvoiceItem
from django.forms import inlineformset_factory

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer']

InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem,
    fields=('product', 'quantity'),
    extra=1, can_delete=True
)
