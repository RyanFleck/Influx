from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

from .models import Institution, Student, Instructor

# Institution


class InstitutionalStudentsInline(admin.TabularInline):
    model = Student


class InstitutionalInstructorsInline(admin.TabularInline):
    model = Instructor


class InstitutionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {'fields': ['name']}),
        ('Address', {'fields': ['address']}),
    ]
    inlines = [InstitutionalInstructorsInline, InstitutionalStudentsInline]

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (InstitutionalInstructorsInline, InstitutionalStudentsInline)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

