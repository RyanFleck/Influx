from django.shortcuts import render
from django.http import HttpResponse, Http404

from .models import Question

# Create your views here.


def index(request):

    questions = Question.objects.order_by('-pub_date')[:5]
    #output = ', '.join([q.question_text for q in questions])
    context = {'questions': questions}

    return render(request, 'index.html', context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist!")

    return render(request, 'detail.html', {'question': question})


def vote(request, question_id):
    return HttpResponse("You are voting on question %s." % question_id)


def results(request, question_id):
    return HttpResponse("Results for question %s." % question_id)
