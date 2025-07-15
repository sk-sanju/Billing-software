from django.contrib import admin
from .models import SalesRecord, CustomerActivity, ProductPerformance

admin.site.register(SalesRecord)
admin.site.register(CustomerActivity)
admin.site.register(ProductPerformance)