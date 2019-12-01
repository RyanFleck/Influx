from django import forms
from functools import reduce
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import InfluxUser, Student, Instructor, Institution, Course, Section, Team
from .forms import RegistrationForm, LoginForm, CourseSetupForm


class LandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "tms/landing.html"

    def get_context_data(self, *args, **kwargs):
        context = super(LandingView, self).get_context_data(*args, **kwargs)
        context['message'] = 'Welcome to the homepage for the InFlux TMS.'
        context['user_section_info'] = self.get_user_section_info()
        self.add_students_without_teams_to_context_by_course(context)
        return context

    def get_user_section_info(self):
        pass

    def add_students_without_teams_to_context_by_course(self, context):
        try:
            self.request.user.instructor
        except Instructor.DoesNotExist:
            return None 

        user = InfluxUser.objects.get(id=self.request.user.id)
        sections = user.instructor.instructing_sections.all()

        for section in sections:
            teams = Team.objects.filter(section=section)
            students = Student.objects.filter(course_sections=section).exclude(teams__in=teams).distinct()
            context[ 'no_team_{}'.format(section.course.course_code ,section.section_code) ] = students



class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = "tms/login.html"
    success_url = reverse_lazy('tms:landing')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('tms/landing')
        return super(LoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        # Given user_id, user_password
        try:
            u = InfluxUser.objects.get(user_id=form.cleaned_data['user_id'])
            print('User: {}'.format(u.username))

            user = authenticate(username=u.username,
                                password=form.cleaned_data['user_password'])

            if (user is not None and user.is_active):
                login(self.request, user)
            else:
                form.add_error('user_password', error=forms.ValidationError(
                    "Password is incorrect."))
                return super().form_invalid(form)

        except InfluxUser.DoesNotExist:
            return super().form_invalid(form)

        return super().form_valid(form)


class RegistrationView(generic.FormView):
    '''RegistrationUI'''

    form_class = RegistrationForm
    template_name = "tms/registration.html"
    success_url = '/'

    def form_valid(self, form):

        user_id = form.cleaned_data['user_id']
        username = "u{}".format(user_id)
        print("Username: {}".format(username))

        InfluxUser.objects.create_user(
            username,
            email=form.cleaned_data['user_email_address'],
            password=form.cleaned_data['user_password'],
            user_id=user_id,
            first_and_given_name=form.cleaned_data['user_full_name'],
            institution=Institution.objects.get(name="University of Ottawa")
        )

        # I'd rather check the first digit of the institutional ID, but this will do for now.
        if (form.cleaned_data['instructor']):
            Instructor.objects.create(
                user=InfluxUser.objects.get(user_id=user_id),
            )

        else:
            Student.objects.create(
                user=InfluxUser.objects.get(user_id=user_id),
            )

        return super().form_valid(form)


def logout(request):
    if request.method == "POST" and request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('tms:login'))
    else:
        return HttpResponseRedirect(request.path_info)


class InfoView(LoginRequiredMixin, generic.ListView):
    template_name = "tms/info.html"
    context_object_name = 'institutions'

    def get_queryset(self):
        return Institution.objects.order_by('name')


class CourseDetailView(generic.DetailView):
    '''Consider breaking some of this logic into a separate class.'''

    model = Course
    template_name = 'tms/info/course.html'
    context_object_name = 'course'

    def get_sections(self, course=None):
        if not course:
            course = super(CourseDetailView, self).get_context_data()['object']
        sections = Section.objects.filter(course=course)
        return sections

    def get_teams(self, course=None):
        if not course:
            course = super(CourseDetailView, self).get_context_data()['object']
        sections = self.get_sections(course=course)
        teams = []
        for section in sections:
            teams += Team.objects.filter(section=section)
        return teams

    def get_students(self, course=None):
        if not course:
            course = super(CourseDetailView, self).get_context_data()['object']
        sections = self.get_sections(course=course)
        return Student.objects.filter(
            course_sections__in=sections).distinct()

    def get_students_not_in_teams(self):
        # This is the course object.
        course = super(CourseDetailView, self).get_context_data()['object']

        sections = self.get_sections(course=course)
        teams = self.get_teams(course=course)
        return Student.objects.filter(
            course_sections__in=sections).exclude(teams__in=teams).distinct()

    def get_student_team_pairs(self):
        # This is the course object.
        course = super(CourseDetailView, self).get_context_data()['object']

        sections = self.get_sections(course=course)
        teams = self.get_teams(course=course)
        students_in_teams = Student.objects.filter(
            course_sections__in=sections, teams__in=teams)

        student_team_pairs = []
        for student in students_in_teams:
            pair = {}
            pair['student'] = student

            for team in student.teams.all():
                for section in sections:
                    if team.section == section:
                        pair['team'] = team
                        break
                        break

            student_team_pairs.append(dict(pair))
            continue

        print(student_team_pairs)
        return student_team_pairs

    def get_context_data(self, *args, **kwargs):
        context = super(CourseDetailView, self).get_context_data(
            *args, **kwargs)

        context['message'] = 'Welcome to the homepage for the InFlux TMS.'
        context['students_not_in_teams'] = self.get_students_not_in_teams()
        context['student_team_pairs'] = self.get_student_team_pairs()
        context['students'] = self.get_students()

        return context


class CourseSetupView(generic.FormView):
    form_class = CourseSetupForm
    template_name = "tms/coursesetup.html"
    success_url = '/tms/landing'

    def get(self, request, *args, **kwargs):

        # Ensure that the user is an instructor.
        if not request.user.instructor:
            return HttpResponseRedirect('/tms/landing')

        # Check if the course exists.
        course = None
        try:
            course = Course.objects.get(id=self.kwargs['pk'])
        except InfluxUser.DoesNotExist:
            return HttpResponseRedirect('/tms/landing')

        # Display the form page.
        return super(CourseSetupView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CourseSetupView, self).get_form_kwargs()
        course = Course.objects.get(id=self.kwargs['pk'])
        kwargs['course_name'] = course.course_code
        first_section = course.section_set.first()
        first_team = first_section.team_set.first()
        kwargs['max_team_members'] = first_team.max_students
        return kwargs

    def form_valid(self, form):
        # Objects we need to validate this form.
        instructor = InfluxUser.objects.get(id=self.request.user.id).instructor
        course = None

        # Validate that the course exists
        try:
            course = Course.objects.get(
                course_code=form.cleaned_data['course'])
        except Course.DoesNotExist:
            form.add_error('course', error=forms.ValidationError(
                "Course does not exist."))
            return super().form_invalid(form)

        # Validate that the instructor teaches the course.
        is_instructor = False
        for section in instructor.instructing_sections.all():
            if section.course == course:
                print('Good')

        if is_instructor:
            form.add_error('course', error=forms.ValidationError(
                "You do not instruct this course."))
            return super().form_invalid(form)

        # Ensure that no affiliated teams have too many members.
        sections = Section.objects.filter(course=course).all()
        print(sections)
        teams = []
        for section in sections:
            teams += Team.objects.filter(section=section)

        # Find minimum max_team_size
        minimum_team_maximum = 0
        largest_team_name = ""
        for team in teams:
            team_size = team.student_set.count()
            if team_size > minimum_team_maximum:
                largest_team_name = team.team_name
                minimum_team_maximum = team_size

        max_change = form.cleaned_data['max_members']
        if max_change < minimum_team_maximum:
            form.add_error('max_members', error=forms.ValidationError(
                "Choose a larger maximum size, or remove students from the largest team, {}, with {} members.".format(largest_team_name, minimum_team_maximum)))
            return super().form_invalid(form)

        # Attempt to change the team parameters.
        self.update_team_information(
            teams=teams,
            max_members=form.cleaned_data['max_members'],
            min_members=form.cleaned_data['min_members'],
            formation_deadline=form.cleaned_data['date']
        )

        self.success_url = "/tms/info/course/{}".format(course.id)
        print("Will redirect to {}".format(self.success_url))
        return super().form_valid(form)

    def update_team_information(self, teams, max_members, min_members, formation_deadline):
        for team in teams:
            print("Updating " + str(team))
            # Update maximum members
            team.max_students = max_members
            team.min_students = min_members
            team.formation_deadline = formation_deadline
            team.save()
        pass

    def get_context_data(self, *args, **kwargs):
        context = super(CourseSetupView, self).get_context_data(
            *args, **kwargs)

        course = Course.objects.get(id=self.kwargs['pk'])
        context['course_code'] = str(course.course_code)

        return context


class SectionDetailView(generic.DetailView):
    model = Section
    template_name = 'tms/info/section.html'
    context_object_name = 'section'

    # TO be implemented.
    def get_students_not_in_team(self):
        pass

    def get_context_data(self, *args, **kwargs):
        context = super(SectionDetailView, self).get_context_data(
            *args, **kwargs)

        # To be implemented.
        context['message'] = 'Welcome to the homepage for the InFlux TMS.'
        context['students_not_in_team'] = ['a', 'b', 'c']

        return context


class TeamDetailView(generic.DetailView):
    model = Team
    template_name = 'tms/info/team.html'
    context_object_name = 'team'
