import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from .models import Question


# Create your tests here.

class QuestionTest(TestCase):
    def test_was_published_recently(self):
        time = timezone.now() + datetime.timedelta(days=10)
        old_time = timezone.now() - datetime.timedelta(days=10)
        correct_time = timezone.now() - datetime.timedelta(hours=2)
        future_question = Question(pub_date=time)
        old_question = Question(pub_date=old_time)
        correct_question = Question(pub_date=correct_time)
        self.assertIs(future_question.was_published_recently(), False)
        self.assertIs(old_question.was_published_recently(), False)
        self.assertIs(correct_question.was_published_recently(), True)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
    def test_index_view_with_no_question(self):
        response = self.client.get(reverse('pills:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pills are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_a_past_question(self):
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('pills:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )

    def test_index_view_with_future_question_and_past_question(self):
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('pills:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_index_view_with_two_past_question(self):
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('pills:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class DetailViewTest(TestCase):
    def test_with_future_question(self):
        question = create_question("Future question.", 10)
        response = self.client.get(reverse('pills:detail', args=(question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_with_past_question(self):
        # 此处，创建问题这个函数，使用的是位置参数，所以不写参数名称也可以↑，当写参数名称但打乱顺序
        # 也是可以的。是Python做的一些优化
        past_question = create_question(days=-5, question_text="Old question")
        url = reverse('pills:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)
