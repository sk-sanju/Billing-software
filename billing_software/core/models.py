from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
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
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        """Ensure quantity does not exceed available stock."""
        if self.product and self.quantity > self.product.stock:
            raise ValidationError(f"Not enough stock for {self.product.name}. "
                                    f"Available: {self.product.stock}, Requested: {self.quantity}")

    def save(self, *args, **kwargs):
        # Validate before saving
        self.clean()

        # Calculate total
        self.total = self.quantity * self.unit_price

        # Save the item first
        super().save(*args, **kwargs)

        # Then reduce stock from product
        if self.product:
            self.product.stock -= self.quantity
            if self.product.stock < 0:
                self.product.stock = 0  # safety fallback
            self.product.save()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

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
from django.db import models
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
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

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


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
