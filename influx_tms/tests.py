from django.test import TestCase
from django.shortcuts import render, get_object_or_404
from .models import InfluxUser, Student, Instructor, Institution

# Create your tests here.


class TestUserCreationTestCaseTest(TestCase):
    def setUp(self):
        InfluxUser.objects.filter(user_id="12345678").delete()
        InfluxUser.objects.filter(user_id="1234567").delete()

    def test_create_a_user(self):

        u = InfluxUser(
            username="u12345678",
            user_id="12345678",
            first_and_given_name="Testothy Jones",
            password="abcde",
            institution=Institution.objects.get(name="University of Ottawa")
        )
        s = Student(
            user=u,
        )
        u.save()
        s.save()
