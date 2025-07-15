from django.contrib import admin
from .models import APILog, APIToken

admin.site.register(APILog)
admin.site.register(APIToken)