from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic

from .models import Question, Choice

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'questions'

    def get_queryset(self):
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    q = get_object_or_404(Question, pk=question_id)

    try:
        # Get choice from POST request!
        c = q.choice_set.get(pk=request.POST['choice'])

    except (KeyError, Choice.DoesNotExist):

        return render(request, 'polls/detail.html', {
            'question': q,
            'error_message': "Please make a selection."
        })

    else:
        c.votes += 1
        c.save()
        return HttpResponseRedirect(reverse('polls:results', args=(q.id,)))
