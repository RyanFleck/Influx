from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import InfluxUser, Student, Instructor
from .forms import RegistrationForm

# Create your views here.

class LoginView(generic.TemplateView):
    template_name = "tms/login.html"

class LandingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "tms/landing.html"

class RegistrationView(generic.FormView):
    form_class = RegistrationForm 
    # user_id, instructor, user_password, user_full_name, user_email_address
    template_name = "tms/registration.html"
    success_url = '/'

    # user_id
    # instructor
    # user_password
    # user_full_name
    # user_email_address
    
    def form_valid(self, form):

        # Debug, print all incoming form fields:
        y = 0
        for x in form.cleaned_data:
            print("{}: {} -> {}".format(y, x, form.cleaned_data[str(x)]))
            y = y + 1

        return super().form_valid(form)
