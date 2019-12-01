from django import forms
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import InfluxUser, Student, Instructor, Institution, Course, Section, Team
from .forms import RegistrationForm, LoginForm, CourseSetupForm

# Create your views here.


class LandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "tms/landing.html"

    def get_context_data(self, *args, **kwargs):
        context = super(LandingView, self).get_context_data(*args, **kwargs)
        context['message'] = 'Welcome to the homepage for the InFlux TMS.'
        return context


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


'''
Below are model-specific views.
'''


class CourseDetailView(generic.DetailView):
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

###############################################################################
###############################################################################


class CourseSetupView(generic.FormView):
    form_class = CourseSetupForm
    template_name = "tms/coursesetup.html"

    def get(self, request, *args, **kwargs):

        # Ensure that the user is an instructor.
        if not request.user.instructor:
            return HttpResponseRedirect('/tms/landing')

        # Check if the course exists.
        try:
            course = Course.objects.get(id=self.kwargs['pk'])
        except InfluxUser.DoesNotExist:
            return HttpResponseRedirect('/tms/landing')

        # Display the form page.
        return super(CourseSetupView, self).get(request, *args, **kwargs)


    def get_form_kwargs(self):
        kwargs = super(CourseSetupView, self).get_form_kwargs()
        kwargs['course_name'] = Course.objects.get(id=self.kwargs['pk']).course_code
        return kwargs

    def form_valid(self, form):

        # Get instructor courses
        print("User " + str(self.request.user.id))
        user = InfluxUser.objects.get(id=self.request.user.id)
        instructor = user.instructor
        course = Course.objects.get(id=self.kwargs['pk'])
        for section in instructor.instructing_sections.all():
            if section.course == course:
                print('Good')
            else:
                return super().form_invalid(form)



        # Attempt to change the team parameters here.
        form.add_error('max_members', error=forms.ValidationError(
            "Cannot be lower than 19"))
        return super().form_invalid(form)

        return super().form_valid(form)
    
    def get_context_data(self, *args, **kwargs):
        context = super(CourseSetupView, self).get_context_data(
            *args, **kwargs)

        course = Course.objects.get(id=self.kwargs['pk'])
        context['course_code'] = str(course.course_code)

        return context

###############################################################################
###############################################################################


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
