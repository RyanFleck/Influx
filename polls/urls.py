from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [

    # Change this to 'poll' after experiment is finished.
    path('', views.index, name='index'),

    # A set of pages for looking at poll questions
    path('<int:question_id>', views.detail, name='detail'),
    path('<int:question_id>/results', views.results, name='results'),
    path('<int:question_id>/vote', views.vote, name='vote'),
]
