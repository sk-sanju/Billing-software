from django.contrib import admin
from .models import Client, Customer, Product

admin.site.register(Client)
admin.site.register(Customer)
admin.site.register(Product)