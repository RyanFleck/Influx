from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse

from .models import Question, Choice

# Create your views here.


def index(request):

    questions = Question.objects.order_by('-pub_date')[:5]
    #output = ', '.join([q.question_text for q in questions])
    context = {'questions': questions}

    return render(request, 'index.html', context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
        # alternatively, get_object_or_404(Question, pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist!")

    return render(request, 'detail.html', {'question': question})


def vote(request, question_id):
    q = get_object_or_404(Question, pk=question_id)

    try:
        # Get choice from POST request!
        c = q.choice_set.get(pk=request.POST['choice'])
    
    except (KeyError, Choice.DoesNotExist):

        return render(request, 'detail.html', {
            'question': q,
            'error_message': "Please make a selection."
        })
    
    else:
        c.votes += 1
        c.save()
        return HttpResponseRedirect(reverse('polls:results', args=(q.id,)))



def results(request, question_id):
    q = get_object_or_404(Question, pk=question_id)
    return render(request, 'results.html', {'question':q})
