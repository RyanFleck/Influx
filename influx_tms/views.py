from django import forms
from functools import reduce
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import InfluxUser, Student, Instructor, Institution, Course, Section, Team
from .forms import RegistrationForm, LoginForm, CourseSetupForm, TeamCreationForm, TeamJoinForm


class LandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "tms/landing.html"

    def get_context_data(self, *args, **kwargs):
        context = super(LandingView, self).get_context_data(*args, **kwargs)
        context['message'] = 'Welcome to the homepage for the InFlux TMS.'
        context['student_data'] = self.get_student_team_data()
        context['instructor_data'] = self.get_instructor_team_data()
        return context

    def get_student_team_data(self):
        try:
            self.request.user.student
        except Student.DoesNotExist:
            return None
        pass

        user = InfluxUser.objects.get(id=self.request.user.id)
        sections = user.student.course_sections.all()
        structure = []

        for section in sections:
            teams = Team.objects.filter(section=section)
            in_a_team = False
            for team in teams:
                if team.student_set.filter(user=user):
                    print("In team " + str(team))
                    in_a_team = True

                    section_structure = {
                        'name': "{}-{}".format(section.course.course_code, section.section_code),
                        'section': section,
                        'inteam': in_a_team,
                        'teamName': team.team_name,
                        'team': team
                    }

                    print(section_structure)
                    structure.append(dict(section_structure))
                    break

            if not in_a_team:
                section_structure = {
                    'name': "{}-{}".format(section.course.course_code, section.section_code),
                    'section': section,
                    'inteam': in_a_team,
                    'teamName': ""
                }

                print(section_structure)
                structure.append(dict(section_structure))

        return structure

    def get_instructor_team_data(self):
        try:
            self.request.user.instructor
        except Instructor.DoesNotExist:
            return None

        user = InfluxUser.objects.get(id=self.request.user.id)
        sections = user.instructor.instructing_sections.all()
        structure = []

        for section in sections:
            teams = Team.objects.filter(section=section)
            no_team = Student.objects.filter(
                course_sections=section).exclude(teams__in=teams).distinct()
            section_structure = {
                'name': "{}-{}".format(section.course.course_code, section.section_code),
                'section': section,
                'teams': teams,
                'not_in_team': no_team,
            }

            print(section_structure)
            structure.append(dict(section_structure))

        return structure


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
        course.min_student_default = form.cleaned_data['min_members']
        course.max_student_default = form.cleaned_data['max_members']
        course.creation_deadline_default = form.cleaned_data['date']
        course.save()
        self.update_team_information(
            teams=teams,
            max_members=form.cleaned_data['max_members'],
            min_members=form.cleaned_data['min_members'],
            formation_deadline=form.cleaned_data['date']
        )

        self.success_url = "/tms/info/course/{}".format(course.id)
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


class TeamCreationFormView(generic.FormView):
    form_class = TeamCreationForm
    template_name = "tms/teamcreation.html"
    success_url = '/tms/landing'

    def get(self, request, *args, **kwargs):

        # Ensure that the user is a student.
        if not request.user.student:
            return HttpResponseRedirect('/tms/landing')

        try:
            Section.objects.get(id=self.kwargs['pk'])
        except Section.DoesNotExist:
            return HttpResponseRedirect('/tms/landing')

        return super(TeamCreationFormView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(TeamCreationFormView, self).get_form_kwargs()
        section = Section.objects.get(id=self.kwargs['pk'])
        kwargs['section_name'] = "{}".format(str(section))
        kwargs['section'] = section
        kwargs['student'] = Student.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):

        section = Section.objects.get(id=self.kwargs['pk'])
        liasion = Student.objects.get(user=self.request.user)
        teammates = form.cleaned_data['teammates']

        # Ensure all teammates are available to be placed in a team.
        students_without_a_team = Student.objects.filter(
            course_sections=section)
        teams = section.team_set.all()

        # Remove students in teams
        for student in students_without_a_team:
            for team in teams:
                if team.student_set.filter(user=student.user).exists():
                    students_without_a_team = students_without_a_team.exclude(
                        user=student.user)

        for mate in teammates:
            if (mate not in students_without_a_team):
                form.add_error('team_name', error=forms.ValidationError(
                    "Form in development."))
                return super().form_invalid(form)

        if liasion not in students_without_a_team:
            form.add_error('team_name', error=forms.ValidationError(
                "You are already in a team!"))
            return super().form_invalid(form)

        # Ensure the name is not a duplicate.

        # Create the team
        newteam = Team.objects.create(
            section=section,
            liasion=liasion,
            team_name=form.cleaned_data['team_name'],
            formation_deadline=section.course.creation_deadline_default,
            min_students=section.course.min_student_default,
            max_students=section.course.max_student_default,
        )
        newteam.save()

        for mate in teammates:
            mate.teams.add(newteam)
            mate.save()

        liasion.teams.add(newteam)
        liasion.save()

        self.success_url = "/tms/info/team/{}".format(newteam.id)

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(TeamCreationFormView, self).get_context_data(
            *args, **kwargs)

        section = Section.objects.get(id=self.kwargs['pk'])
        context['section'] = section

        return context


class TeamJoinFormView(generic.FormView):
    form_class = TeamJoinForm
    template_name = "tms/teamjoin.html"
    success_url = '/tms/landing'

    def get(self, request, *args, **kwargs):

        # Ensure that the user is a student.
        if not request.user.student:
            return HttpResponseRedirect('/tms/landing')

        try:
            Section.objects.get(id=self.kwargs['pk'])
        except Section.DoesNotExist:
            return HttpResponseRedirect('/tms/landing')

        return super(TeamJoinFormView, self).get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(TeamJoinFormView, self).get_form_kwargs()
        section = Section.objects.get(id=self.kwargs['pk'])
        kwargs['section_name'] = "{}".format(str(section))
        kwargs['section'] = section
        kwargs['student'] = Student.objects.get(user=self.request.user)
        return kwargs

    def form_valid(self, form):

        section = Section.objects.get(id=self.kwargs['pk'])
        teammates = form.cleaned_data['team']
        student = Student.objects.get(user=self.request.user)
        team = form.cleaned_data['team']

        # Check if the student is already in a team in this section.

        # Check if the student is already pending entry into a team.

        # Add student to pending_students
        team.pending_students.add(student)
        team.save()

        self.success_url = "/tms/info/team/{}".format(team.id)
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(TeamJoinFormView, self).get_context_data(
            *args, **kwargs)

        section = Section.objects.get(id=self.kwargs['pk'])
        context['section'] = section

        return context

# Small method to add a user to a team.
def add_to_team(request, studentid, teamid):
    if request.method == "POST" and request.user.is_authenticated:

        team = None
        request_student = None
        add_user = None
        add_student = None

        try:
            team = Team.objects.get(id=teamid)
            request_student = request.user.student
            add_user = InfluxUser.objects.get(id=studentid)
            add_student = Student.objects.get(user=add_user)
        except:
            print("Failed to fetch objects.")

        # TODO: Tons of additional checks need to be made here.
        # Check if student is in any other teams in this section.
        # Check if requestor is liasion for this team.
        # Only show buttons to liasion.

        team.pending_students.remove(add_student)
        add_student.teams.add(team)

        # Dirty and hardcoded.
        return HttpResponseRedirect('/tms/info/team/{}/'.format(teamid))