from django.urls import path, include

from . import views


app_name = 'tms'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('register/', views.RegistrationView.as_view(), name='registration'),
    path('tms/landing/', views.LandingView.as_view(), name='landing'),
    path('tms/info/', views.InfoView.as_view(), name='info'),
    path('tms/info/course/<int:pk>/',
         views.CourseDetailView.as_view(), name='courseinfo'),
    path('tms/info/course/<int:pk>/setup/',
         views.CourseSetupView.as_view(), name='coursesetup'),
    path('tms/info/team/<int:pk>/',
         views.TeamDetailView.as_view(), name='teaminfo'),
    path('tms/info/section/<int:pk>/createteam/',
         views.TeamCreationFormView.as_view(), name='createteam'),
    path('tms/info/section/<int:pk>/jointeam/',
         views.TeamJoinFormView.as_view(), name='jointeam'),
    path('tms/info/section/<int:pk>/',
         views.SectionDetailView.as_view(), name='sectioninfo'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logout, name='logout'),
    path('add_to_team/<int:studentid>/<int:teamid>', views.add_to_team, name='add-to-team'),
]
