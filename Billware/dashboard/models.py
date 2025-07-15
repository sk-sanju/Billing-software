from django.db import models
from core.models import Client

class SalesRecord(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_invoices = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.client.name} - {self.date}"


class CustomerActivity(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    purchases_count = models.PositiveIntegerField()
    last_purchase_date = models.DateField()

    def __str__(self):
        return f"{self.customer_name} Activity"


class ProductPerformance(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    units_sold = models.PositiveIntegerField()
    revenue_generated = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} Performance"
