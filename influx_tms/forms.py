# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import InfluxUser


class InfluxUserCreationForm(UserCreationForm):

    class Meta:
        model = InfluxUser
        fields = ('user_id', 'first_and_given_name', 'email')


class InfluxUserUpdateForm(UserChangeForm):

    class Meta:
        model = InfluxUser
        fields = ('user_id', 'first_and_given_name', 'email')
