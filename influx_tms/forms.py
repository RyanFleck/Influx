# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import InfluxUser
from django.db import transaction


class InfluxUserCreationForm(UserCreationForm):

    class Meta:
        model = InfluxUser
        fields = ('user_id', 'first_and_given_name', 'email')


class InfluxUserUpdateForm(UserChangeForm):

    class Meta:
        model = InfluxUser
        fields = ('user_id', 'first_and_given_name', 'email')


class RegistrationForm(forms.Form):
    # User identification (employee or student number)
    user_id = forms.CharField(label='User ID', max_length=20, initial="1234567")
    instructor = forms.BooleanField(required=False, label="Instructor")
    # Login Password
    user_password = forms.CharField(
        widget=forms.PasswordInput, label='Password', initial="nicoandthevelvetunderground")
    #Name (First and Given)
    user_full_name = forms.CharField(label="Full Name", max_length=200, initial="Neato Burrito")
    # Email address
    user_email_address = forms.EmailField(initial="Neato.Burrito@evil.google.corp")

class LoginForm(forms.Form):
    user_id = forms.CharField(label='User ID', max_length=20, initial="1234567")
    user_password = forms.CharField(
        widget=forms.PasswordInput, label='Password', initial="nicoandthevelvetunderground")
