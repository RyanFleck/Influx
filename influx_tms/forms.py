# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import InfluxUser
from django.db import transaction


class RegistrationForm(forms.Form):
    # User identification (employee or student number)
    user_id = forms.CharField(
        label='User ID', max_length=20, initial="1234567")
    instructor = forms.BooleanField(required=False, label="Instructor")
    # Login Password
    user_password = forms.CharField(
        widget=forms.PasswordInput, label='Password', initial="nicoandthevelvetunderground")
    #Name (First and Given)
    user_full_name = forms.CharField(
        label="Full Name", max_length=200, initial="Neato Burrito")
    # Email address
    user_email_address = forms.EmailField(
        initial="Neato.Burrito@evil.google.corp")

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        user_id = cleaned_data.get("user_id")
        instructor = cleaned_data.get("instructor")

        # Check if user is already in system.
        try:
            user = InfluxUser.objects.get(user_id=user_id)
            if (user):
                raise forms.ValidationError(
                    "The User ID has already been registered.")
        except InfluxUser.DoesNotExist:
            pass

        if (user_id[0] == '1' and not instructor):
            raise forms.ValidationError(
                "Only instructor userIDs start with a 1.")

        if (user_id[0] != '1' and instructor):
            raise forms.ValidationError(
                "Instructor userIDs always start with a 1.")

        return cleaned_data


class LoginForm(forms.Form):
    user_id = forms.CharField(
        label='User ID', max_length=20, initial="1234567")
    user_password = forms.CharField(
        widget=forms.PasswordInput, label='Password')

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        user_id = cleaned_data.get("user_id")

        try:
            InfluxUser.objects.get(user_id=user_id)
        except InfluxUser.DoesNotExist:
            raise forms.ValidationError("The User ID has not been registered.")

        return cleaned_data


class InfluxUserCreationForm(UserCreationForm):

    class Meta:
        model = InfluxUser
        fields = ('user_id', 'first_and_given_name', 'email')


class InfluxUserUpdateForm(UserChangeForm):

    class Meta:
        model = InfluxUser
        fields = ('user_id', 'first_and_given_name', 'email')
