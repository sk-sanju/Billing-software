from django.contrib import admin
from .models import Tax, Discount, InvoiceDetail, InvoiceProduct

admin.site.register(Tax)
admin.site.register(Discount)
admin.site.register(InvoiceDetail)
admin.site.register(InvoiceProduct)