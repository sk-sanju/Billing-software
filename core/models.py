from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # e.g. 18.00 for 18%
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        """Ensure quantity does not exceed available stock, accounting for original quantity if editing."""
        orig_qty = 0
        if self.pk:
            try:
                orig_item = InvoiceItem.objects.get(pk=self.pk)
                if orig_item.product == self.product:
                    orig_qty = orig_item.quantity
            except InvoiceItem.DoesNotExist:
                pass
        
        if self.product and self.quantity > (self.product.stock + orig_qty):
            raise ValidationError(
                f"Not enough stock for {self.product.name}. "
                f"Available: {self.product.stock + orig_qty}, Requested: {self.quantity}"
            )

    def save(self, *args, **kwargs):
        self.clean()
        
        # Calculate total
        self.total = self.quantity * self.unit_price

        orig_qty = 0
        orig_product = None
        if self.pk:
            try:
                orig_item = InvoiceItem.objects.get(pk=self.pk)
                orig_qty = orig_item.quantity
                orig_product = orig_item.product
            except InvoiceItem.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Update inventory stock levels
        if self.product:
            if orig_product == self.product:
                qty_diff = self.quantity - orig_qty
                if qty_diff != 0:
                    self.product.stock -= qty_diff
                    self.product.save()
            else:
                if orig_product:
                    orig_product.stock += orig_qty
                    orig_product.save()
                self.product.stock -= self.quantity
                self.product.save()
        elif orig_product:
            orig_product.stock += orig_qty
            orig_product.save()

    def delete(self, *args, **kwargs):
        # Restore stock on deletion
        if self.product:
            self.product.stock += self.quantity
            self.product.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        prod_name = self.product.name if self.product else "Deleted Product"
        return f"{prod_name} x {self.quantity}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer')
    ])
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Payment for Invoice #{self.invoice.invoice_number}"
