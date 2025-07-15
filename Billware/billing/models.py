from django.db import models
from core.models import Client, Customer, Product

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


class Discount(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"


class InvoiceDetail(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True)
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='invoices/pdf/', null=True, blank=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.customer.name}"


class InvoiceProduct(models.Model):
    invoice = models.ForeignKey(InvoiceDetail, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
