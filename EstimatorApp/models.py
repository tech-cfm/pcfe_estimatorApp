from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # last_name = models.CharField(max_length=50)
    footprint_history = models.JSONField(default=dict)
    # last_login = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"


class Meta:
    ordering = ['user']
