from django.urls import path

from . import views


app_name = 'tms'
urlpatterns = [

    # Change this to 'poll' after experiment is finished.
    path('', views.IndexView.as_view(), name='index'),
]
