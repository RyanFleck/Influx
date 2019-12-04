from django.db import models
from django.db.models import Q
import datetime

from django.contrib.auth.models import AbstractUser

# Create your models here.


class Institution(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Course(models.Model):
    institution = models.ForeignKey(
        Institution, blank=True, null=True, on_delete=models.SET_NULL)
    course_code = models.CharField(max_length=200)

    min_student_default = models.IntegerField(default=0)
    max_student_default = models.IntegerField(default=4)
    creation_deadline_default = models.DateTimeField(
        'creation deadline default', blank=True,
        default=datetime.date.today()+datetime.timedelta(days=+30))

    def __str__(self):
        return self.course_code


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_code = models.CharField(max_length=50)

    def __str__(self):
        return "{}-{}".format(self.course.course_code, self.section_code)


class Team(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=200)
    creation_date = models.DateTimeField(
        'date created', auto_now_add=True, blank=True)
    formation_deadline = models.DateTimeField('formation deadline')

    liasion = models.ForeignKey(
        'Student', on_delete=models.SET_NULL, blank=True, null=True)

    min_students = models.IntegerField(default=0)
    max_students = models.IntegerField(default=4)

    pending_students = models.ManyToManyField(
        'Student', related_name='pending_students', blank=True)

    STATUS_CHOICES = (
        ("INCOMPLETE", "Incomplete"),
        ("COMPLETE", "Complete"),
    )

    team_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="INCOMPLETE")

    def save(self, *args, **kwargs):
        print("Saving team...")
        # TODO: Set first member as liasion.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.team_name


class InfluxUser(AbstractUser):
    user_id = models.CharField(max_length=50)
    first_and_given_name = models.CharField(max_length=200)
    institution = models.ForeignKey(
        Institution, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.first_and_given_name


class Instructor(models.Model):
    user = models.OneToOneField(
        InfluxUser, on_delete=models.CASCADE, primary_key=True)

    instructing_sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.user.first_and_given_name


class Student(models.Model):
    user = models.OneToOneField(
        InfluxUser, on_delete=models.CASCADE, primary_key=True)

    program_of_study = models.CharField(max_length=50, null=True, blank=True)

    teams = models.ManyToManyField(Team)
    course_sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.user.first_and_given_name
