from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extend Django's built-in User model with extra fields if needed.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username
