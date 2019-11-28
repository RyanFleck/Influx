from django.db import models

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

    def __str__(self):
        return self.course_code


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_code = models.CharField(max_length=50)

    def __str__(self):
        return "{}-{}".format(self.course.course_code,self.section_code)


class Team(models.Model):
    # ID will be provided when the teams are created.
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=200)
    creation_date = models.DateTimeField('date created')
    formation_deadline = models.DateTimeField('formation deadline')

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

    sections = models.ManyToManyField(Section)

    def __str__(self):
        return self.user.first_and_given_name


class Student(models.Model):
    user = models.OneToOneField(
        InfluxUser, on_delete=models.CASCADE, primary_key=True)

    teams = models.ManyToManyField(Team)

    def __str__(self):
        return self.user.first_and_given_name
