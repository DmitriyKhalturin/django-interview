from django.test import tag
from django.urls import include, path, reverse
from rest_framework.test import URLPatternsTestCase

from common.django_rest_framework.tests import AuthAPITestCase
from interview.apps.questions.models import Question


@tag('api')
class LineFlowTestCase(AuthAPITestCase, URLPatternsTestCase):

    urlpatterns = [
        path(r'topics/', include('interview.apps.topics.urls')),
        path(r'questions/', include('interview.apps.questions.urls')),
        path(r'answers/', include('interview.apps.answers.urls')),
        path(r'users-answers/', include('interview.apps.users_answers.urls')),
    ]

    @AuthAPITestCase.authenticate
    def test_001_create_1_topic(self):
        response = self.client.post(
            reverse('topics:topics-list'),
            data={
                'title': 'Topic #1.',
                'start_date': '2020-08-10',
                'finish_date': '2020-08-15',
                'description': 'Topic description.',
            },
            format='json'
        )
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)
        topic_1_id = response.data.get('id', None)
        assert topic_1_id is not None
        self.storage.update({'topic_1_id': topic_1_id})

    @AuthAPITestCase.authenticate
    def test_002_create_2_topic(self):
        response = self.client.post(
            reverse('topics:topics-list'),
            data={
                'title': 'Topic #2.',
                'start_date': '2020-08-15',
                'finish_date': '2020-08-25',
                'description': 'Topic description.',
            },
            format='json'
        )
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)
        topic_2_id = response.data.get('id', None)
        assert topic_2_id is not None
        self.storage.update({'topic_2_id': topic_2_id})

    @AuthAPITestCase.authenticate
    def test_003_get_2_topics(self):
        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)
        assert (len(response.data) == 2)

    @AuthAPITestCase.authenticate
    def test_004_update_1_topic_field(self):
        topic_1_id = self.storage.get('topic_1_id', None)
        assert topic_1_id is not None

        value_update_field = 'Updated field.'
        response = self.client.put(
            reverse('topics:topics-detail', args=[topic_1_id]),
            data={
                'description': value_update_field,
            },
            format='json'
        )
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)
        assert (response.data.get('description') == value_update_field)

        response = self.client.get(reverse('topics:topics-detail', args=[topic_1_id]))
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)
        assert (response.data.get('description') == value_update_field)

    @AuthAPITestCase.authenticate
    def test_005_catch_exception_update_topic_field(self):
        topic_1_id = self.storage.get('topic_1_id', None)
        assert topic_1_id is not None

        response = self.client.put(
            reverse('topics:topics-detail', args=[topic_1_id]),
            data={
                'start_date': '2020-08-11',
            },
            format='json'
        )
        assert (response.status_code == 400)

    @AuthAPITestCase.authenticate
    def test_006_delete_1_topic_from_2(self):
        topic_2_id = self.storage.get('topic_2_id', None)
        assert topic_2_id is not None

        response = self.client.delete(reverse('topics:topics-detail', args=[topic_2_id]))
        assert (response.status_code == 200)

        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)
        assert (len(response.data) == 1)

    @AuthAPITestCase.authenticate
    def test_007_create_question_with_answers(self):
        topic_1_id = self.storage.get('topic_1_id', None)
        assert topic_1_id is not None

        response = self.client.post(
            reverse('questions:questions-list'),
            data={
                'text': 'Question #1.',
                'type': Question.ONE_OPTION,
                'topic_id': topic_1_id,
                'answers': [
                    'One answer.',
                    'Two answer.',
                    'Three answer.',
                ],
            },
            format='json'
        )
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)
        question_1_id = response.data.get('id', None)
        assert question_1_id is not None
        self.storage.update({'question_1_id': question_1_id})

    @AuthAPITestCase.authenticate
    def test_008_catch_exception_create_questions(self):
        topic_1_id = self.storage.get('topic_1_id', None)
        assert topic_1_id is not None

        response = self.client.post(
            reverse('questions:questions-list'),
            data={
                'text': 'Question #2.',
                'type': Question.MULTIPLE_OPTION,
                'topic_id': topic_1_id,
                'answers': [],
            },
            format='json'
        )
        assert (response.status_code == 400)

        response = self.client.post(
            reverse('questions:questions-list'),
            data={
                'text': 'Question #3.',
                'type': Question.CUSTOM_OPTION,
                'topic_id': topic_1_id,
                'answers': [
                    'One answer.',
                    'Two answer.',
                    'Three answer.',
                ],
            },
            format='json'
        )
        assert (response.status_code == 400)

    @AuthAPITestCase.authenticate
    def test_009_update_question(self):
        question_1_id = self.storage.get('question_1_id', None)
        assert question_1_id is not None

        response = self.client.put(
            reverse('questions:questions-detail', args=[question_1_id]),
            data={
                'text': 'Update question.',
                'type': Question.CUSTOM_OPTION,
            },
            format='json'
        )
        assert (response.status_code == 200)
        answers = response.data.get('answers')
        assert isinstance(answers, list)
        assert (len(answers) == 0)

        response = self.client.put(
            reverse('questions:questions-detail', args=[question_1_id]),
            data={
                'type': Question.MULTIPLE_OPTION,
                'answers': [
                    'One answer.',
                    'Two answer.',
                    'Three answer.',
                ],
            },
            format='json'
        )
        assert (response.status_code == 200)
        answers = response.data.get('answers')
        assert isinstance(answers, list)
        assert (len(answers) > 0)

        response = self.client.put(
            reverse('questions:questions-detail', args=[question_1_id]),
            data={
                'type': Question.ONE_OPTION,
                'answers': [
                    'Only one variant.',
                ],
            },
            format='json'
        )
        assert (response.status_code == 200)
        answers = response.data.get('answers')
        assert isinstance(answers, list)
        assert (len(answers) == 1)

        answer_1_id = answers[0].get('id')
        assert answer_1_id is not None
        self.storage.update({'answer_1_id': answer_1_id})

    @AuthAPITestCase.authenticate
    def test_010_create_user_answer(self):
        question_1_id = self.storage.get('question_1_id', None)
        answer_1_id = self.storage.get('answer_1_id', None)
        assert question_1_id is not None
        assert answer_1_id is not None

        response = self.client.post(
            reverse('users-answers:users-answers-list'),
            data={
                'user_id': 666,
                'question_id': question_1_id,
                'answer_id': answer_1_id,
            },
            format='json'
        )
        assert (response.status_code == 200)

    @AuthAPITestCase.authenticate
    def test_011_delete_question(self):
        question_1_id = self.storage.get('question_1_id', None)
        assert question_1_id is not None

        response = self.client.delete(reverse('questions:questions-detail', args=[question_1_id]))
        assert (response.status_code == 200)
