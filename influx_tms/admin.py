from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Register your models here.

# from .models import Institution, Student, Instructor
from .models import InfluxUser
from .forms import InfluxUserCreationForm, InfluxUserUpdateForm


class InfluxUserAdmin(UserAdmin):
    add_form = InfluxUserCreationForm
    form = InfluxUserUpdateForm
    model = InfluxUser
    list_display = ['user_id', 'first_and_given_name', 'email']

admin.site.register(InfluxUser, InfluxUserAdmin)