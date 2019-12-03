# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import InfluxUser, Course, Student, Team
from django.db import transaction

import datetime


class RegistrationForm(forms.Form):
    # User identification (employee or student number)
    user_id = forms.CharField(
        label='User ID', max_length=20)
    instructor = forms.BooleanField(required=False, label="Instructor")
    # Login Password
    user_password = forms.CharField(
        widget=forms.PasswordInput, label='Password')
    #Name (First and Given)
    user_full_name = forms.CharField(
        label="Full Name", max_length=200)
    # Email address
    user_email_address = forms.EmailField(
        initial="student@university.com")

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


class CourseSetupForm(forms.Form):
    course = forms.CharField(label='static')

    min_members = forms.IntegerField(label="Minimum Team Members", initial=1)
    max_members = forms.IntegerField(label="Maximum Team Members", initial=4)

    date = forms.DateField(label="Team Creation Deadline",
                           initial=datetime.date.today()+datetime.timedelta(days=+14))

    def clean(self):
        cleaned_data = super(CourseSetupForm, self).clean()
        # raise forms.ValidationError("The form is in development")

        # Date must not be in the past.

        return cleaned_data

    def __init__(self, *args, **kwargs):

        course_name = kwargs.pop('course_name')
        max_team_members = kwargs.pop('max_team_members')

        context = super(CourseSetupForm, self).__init__(
            *args, **kwargs)

        if course_name:
            self.fields['course'] = forms.CharField(
                label='Course Name', initial=course_name)

        if max_team_members:
            self.fields['max_members'] = forms.IntegerField(
                label="Maximum Team Members", initial=max_team_members)


class LoginForm(forms.Form):
    user_id = forms.CharField(
        label='User ID', max_length=20)
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



class TeamCreationForm(forms.Form):
    team_name = forms.CharField(label='Team Name')
    teammates = forms.ModelMultipleChoiceField(
        label='Teammates', queryset=Student.objects.all(), required=False)

    def clean(self):
        cleaned_data = super(TeamCreationForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):

        section_name = kwargs.pop('section_name')
        section = kwargs.pop('section')
        student = kwargs.pop('student')
        context = super(TeamCreationForm, self).__init__(
            *args, **kwargs)

        # The form can only show students that are in the same section,
        #  and are not in another team.
        students_without_a_team = Student.objects.filter(
            course_sections=section).exclude(user=student.user)

        teams = section.team_set.all()
        # Remove students in teams
        for student in students_without_a_team:
            for team in teams:
                if team.student_set.filter(user=student.user).exists():
                    students_without_a_team = students_without_a_team.exclude(
                        user=student.user)

        self.fields['teammates'].queryset = students_without_a_team


###############################################################################
###############################################################################

class TeamJoinForm(forms.Form):
    team = forms.ModelChoiceField(label='Join Team', queryset=Team.objects.all())

    def clean(self):
        cleaned_data = super(TeamJoinForm, self).clean()

        return cleaned_data

    def __init__(self, *args, **kwargs):

        section_name = kwargs.pop('section_name')
        section = kwargs.pop('section')
        student = kwargs.pop('student')
        context = super(TeamJoinForm, self).__init__(
            *args, **kwargs)
        
        filtered_teams = Team.objects.filter(section=section)

        self.fields['team'].queryset = filtered_teams 