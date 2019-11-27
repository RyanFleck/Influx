from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.

class Institution(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)

class InfluxUser(AbstractUser):
    user_id = models.CharField(max_length=200)
    first_and_given_name = models.CharField(max_length=200)