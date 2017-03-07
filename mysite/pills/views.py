from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, Choice


# Create your views here.
def index(request):
    lasted_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {
        'lasted_question_list': lasted_question_list
    }
    return render(request, "pills/index.html", context)


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "pills/detail.html", {"question": question})


def result(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "pills/results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExit):
        return render(request, 'pills/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice."
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('pills:result', args=(question_id,)))
