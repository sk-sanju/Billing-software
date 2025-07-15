from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    USER_ROLES = (
        ('owner', 'Owner'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='staff')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Permission(models.Model):
    role = models.CharField(max_length=20)
    can_create_invoice = models.BooleanField(default=False)
    can_manage_products = models.BooleanField(default=False)
    can_manage_customers = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)

    def __str__(self):
        return f"Permissions for {self.role}"
