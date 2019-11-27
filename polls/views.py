from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Hello, world, this is a poll.")

def detail(request, question_id):
    return HttpResponse("This is question %s." % question_id)

def vote(request, question_id):
    return HttpResponse("You are voting on question %s." % question_id)

def results(request, question_id):
    return HttpResponse("Results for question %s." % question_id)