from django import forms
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth import login, authenticate
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


    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('tms/landing')
        return super(LoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        # Given user_id, user_password
        try:
            u = InfluxUser.objects.get(user_id=form.cleaned_data['user_id'])
            print('User: {}'.format(u.username))

            user = authenticate(username=u.username, password=form.cleaned_data['user_password'])

            if (user is not None and user.is_active):
                login(self.request, user)
            else:
                form.add_error('user_password', error=forms.ValidationError("Password is incorrect."))
                return super().form_invalid(form)

        except InfluxUser.DoesNotExist:
            return super().form_invalid(form)

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

def logout(request):
    if request.method == "POST" and request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('tms:login'))
    else:
        return HttpResponseRedirect(request.path_info)