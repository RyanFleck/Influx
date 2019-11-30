from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Register your models here.

# from .models import Institution, Student, Instructor
from .models import InfluxUser, Course, Section, Team, Institution, Instructor, Student
from .forms import InfluxUserCreationForm, InfluxUserUpdateForm


class InfluxUserAdmin(UserAdmin):
    add_form = InfluxUserCreationForm
    form = InfluxUserUpdateForm
    model = InfluxUser
    list_display = ['user_id', 'first_and_given_name', 'username', 'email']


admin.site.register(InfluxUser, InfluxUserAdmin)

admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Team)
admin.site.register(Institution)
admin.site.register(Instructor)
admin.site.register(Student)
