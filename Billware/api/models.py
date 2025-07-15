from django.db import models
from django.contrib.auth.models import User

class APILog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    request_method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    request_data = models.TextField(null=True, blank=True)
    response_data = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.endpoint} - {self.status_code}"


class APIToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Token for {self.user.username}"
