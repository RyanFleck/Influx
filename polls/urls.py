from django.urls import path

from . import views


app_name = 'polls'
urlpatterns = [

    # Change this to 'poll' after experiment is finished.
    path('', views.IndexView.as_view(), name='index'),

    # A set of pages for looking at poll questions
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
