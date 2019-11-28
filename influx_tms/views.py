from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import InfluxUser, Student, Instructor, Institution
from .forms import RegistrationForm, LoginForm

# Create your views here.


class LandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "tms/landing.html"


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = "tms/login.html"
    success_url = reverse_lazy('tms:landing')

    def form_valid(self, form):

        # Debug, print all incoming form fields:
        y = 0
        for x in form.cleaned_data:
            print("{}: {} -> {}".format(y, x, form.cleaned_data[str(x)]))
            y = y + 1

        return super().form_valid(form)


class RegistrationView(generic.FormView):
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
