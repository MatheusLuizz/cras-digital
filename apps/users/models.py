from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    document = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=255, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, default="Paulista")
    state = models.CharField(max_length=2, default="PE")
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    is_vulnerable = models.BooleanField(default=False)
    cadUnico_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
