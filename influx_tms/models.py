from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class Institution(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True)
    program_of_study = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100)


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True)
    instructor_id = models.CharField(max_length=100)
