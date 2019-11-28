from django.urls import path, include

from . import views


app_name = 'tms'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('register/', views.RegistrationView.as_view(), name='registration'),
    path('tms/landing/', views.LandingView.as_view(), name='landing'),
    path('tms/info/', views.InfoView.as_view(), name='info'),
    path('logout/', views.logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]
