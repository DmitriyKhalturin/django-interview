from datetime import datetime, timedelta
from unittest import TestCase

from django.contrib.auth.models import User
from django.test import tag
from django.urls import reverse
from factory import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from interview.apps.questions.models import Question
from interview.apps.topics.views import UserTopicType
from interview.tests.factories import TopicFactory, QuestionFactory, AnswerFactory


class AuthApiTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.client = cls.client_class()
        cls.user = User.objects.create_superuser('admin', 'admin@mail.com', 'passwd123')
        cls.token = Token.objects.create(user=cls.user)

    def authenticate(self):
        self.client.force_authenticate(user=self.user, token=self.token)

    def unauthenticate(self):
        self.client.force_authenticate(user=None, token=None)


class DatabaseFilling(TestCase):
    """
    Filling database. Create: 3 topics, 3 question with 3 answers for topic.
    """
    def setUp(self) -> None:
        super().setUp()

        for _ in range(3):
            topic = TopicFactory()
            for _ in range(3):
                question = QuestionFactory(topic=topic)
                for _ in range(3):
                    AnswerFactory(question=question)


def assert_list(value):
    assert isinstance(value, list)
    assert value


class TopicHelper(object):

    client: APIClient

    def _get_topics_count(self) -> int:
        """
        Get Topics count. ATTENTION! Before call this method, make authentication.
        :return: topics count.
        """
        __response = self.client.get(reverse('topics:topics-list'))
        assert (__response.status_code == 200)
        assert isinstance(__response.data, list)
        return len(__response.data)

    def _get_topics(self, filter_func, *keys) -> list:
        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert_list(response.data)

        topic = filter_func(response.data)
        assert isinstance(topic, dict)

        return list(map(lambda key: topic.get(key, None), *keys))

    def _get_first_topic(self, *keys) -> list:
        """
        Get first Topic. ATTENTION! Before call this method, make authentication.
        :param keys: list keys which will be returned.
        :return: values from topic object.
        """
        return self._get_topics(
            lambda topics: topics[0],
            keys
        )

    def _get_topic_by_id(self, topic_id, *keys) -> list:
        """
        Get topic by id. ATTENTION! Before call this method, make authentication.
        :param keys: list keys which will be returned.
        :return: values from topic object.
        """
        return self._get_topics(
            lambda topics: next(iter(filter(lambda topic: topic.get('id', None) == topic_id, topics))),
            keys
        )

    def _get_users_topics(self, user_id, is_active_not_passed=True) -> list:
        response = self.client.get(
            reverse('users-topics-list'),
            data={
                'type': (UserTopicType.ACTIVE.value if is_active_not_passed else UserTopicType.PASSED.value),
                'user_id': user_id,
            }
        )
        assert (response.status_code == 200)
        topics = response.data
        assert isinstance(topics, list)

        return topics


@tag('api')
class AdminApiFlowTestCase(AuthApiTestCase, DatabaseFilling, TopicHelper):

    def setUp(self) -> None:
        super().setUp()

        self.authenticate()

    def test_create_topics(self):
        topics_count = self._get_topics_count()

        for i in range(3):
            response = self.client.post(
                reverse('topics:topics-list'),
                data={
                    'title': 'Topic #%d.' % i,
                    'start_date': datetime.now().strftime('%Y-%m-%d'),
                    'finish_date': (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d'),
                    'description': Faker('text', max_nb_chars=512).generate(),
                },
                format='json'
            )
            assert (response.status_code == 200)

        assert (topics_count + 3 == self._get_topics_count())

    def test_get_and_clear_topics(self):
        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        topics = response.data
        assert_list(topics)

        for topic_id in [topic['id'] for topic in topics]:
            response = self.client.delete(reverse('topics:topics-detail', args=[topic_id]))
            assert (response.status_code == 200)

        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)
        assert not response.data

    def test_update_topic_field(self):
        (first_topic_id,) = self._get_first_topic('id')

        value_update_field = 'Updated field.'
        response = self.client.put(
            reverse('topics:topics-detail', args=[first_topic_id]),
            data={
                'description': value_update_field,
            },
            format='json'
        )
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)
        assert (response.data.get('description') == value_update_field)

        response = self.client.get(reverse('topics:topics-detail', args=[first_topic_id]))
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)
        assert (response.data.get('description') == value_update_field)

    def test_catch_exception_update_topic_field(self):
        topics_count = self._get_topics_count()
        (first_topic_id,) = self._get_first_topic('id')

        response = self.client.put(
            reverse('topics:topics-detail', args=[first_topic_id]),
            data={
                'start_date': (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d'),
            },
            format='json'
        )
        assert (response.status_code == 400)
        assert (topics_count == self._get_topics_count())

    def test_delete_one_topic(self):
        topics_count = self._get_topics_count()
        (first_topic_id,) = self._get_first_topic('id')

        response = self.client.delete(reverse('topics:topics-detail', args=[first_topic_id]))
        assert (response.status_code == 200)
        assert (topics_count - 1 == self._get_topics_count())

    def test_create_questions(self):
        (first_topic_id,) = self._get_first_topic('id')

        response = self.client.post(
            reverse('questions:questions-list'),
            data={
                'text': 'Question #X.',
                'type': Question.ONE_OPTION,
                'topic_id': first_topic_id,
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
        question_x_id = response.data.get('id', None)
        assert question_x_id is not None

        response = self.client.get(reverse('topics:topics-detail', args=[first_topic_id]))
        assert (response.status_code == 200)
        assert isinstance(response.data, dict)

        topic_questions = response.data.get('questions', None)
        assert_list(topic_questions)

        question_x = list(filter(lambda question: question.get('id', None) == question_x_id, topic_questions))
        assert question_x
        assert question_x[0].get('answers', None)

    def test_catch_exception_create_questions(self):
        (first_topic_id, after_first_topic_questions,) = self._get_first_topic('id', 'questions')

        response = self.client.post(
            reverse('questions:questions-list'),
            data={
                'text': 'Question #X.',
                'type': Question.MULTIPLE_OPTION,
                'topic_id': first_topic_id,
                'answers': [],
            },
            format='json'
        )
        assert (response.status_code == 400)

        response = self.client.post(
            reverse('questions:questions-list'),
            data={
                'text': 'Question #X.',
                'type': Question.CUSTOM_OPTION,
                'topic_id': first_topic_id,
                'answers': [
                    'One answer.',
                    'Two answer.',
                    'Three answer.',
                ],
            },
            format='json'
        )
        assert (response.status_code == 400)
        (before_first_topic_questions,) = self._get_topic_by_id(first_topic_id, 'questions')
        assert (len(after_first_topic_questions) == len(before_first_topic_questions))

    def test_update_question(self):
        (first_topic_id, first_topic_questions,) = self._get_first_topic('id', 'questions')
        assert_list(first_topic_questions)
        first_question_id = first_topic_questions[0].get('id', None)
        assert first_question_id is not None

        def __test_answers(data, assert_func) -> None:
            answers = data.get('answers')
            assert isinstance(answers, list)
            assert assert_func(answers)

        response = self.client.put(
            reverse('questions:questions-detail', args=[first_question_id]),
            data={
                'text': 'Update question.',
                'type': Question.CUSTOM_OPTION,
            },
            format='json'
        )
        assert (response.status_code == 200)
        __test_answers(response.data, lambda answers: len(answers) == 0)

        response = self.client.put(
            reverse('questions:questions-detail', args=[first_question_id]),
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
        __test_answers(response.data, lambda answers: len(answers) > 0)

        response = self.client.put(
            reverse('questions:questions-detail', args=[first_question_id]),
            data={
                'type': Question.ONE_OPTION,
                'answers': [
                    'Only one variant.',
                ],
            },
            format='json'
        )
        assert (response.status_code == 200)
        first_topic_first_question_answers_count = 1
        __test_answers(response.data, lambda answers: len(answers) == first_topic_first_question_answers_count)

        (first_topic_questions,) = self._get_topic_by_id(first_topic_id, 'questions')
        assert_list(first_topic_questions)

        first_question = list(filter(
            lambda question: question.get('id', None) == first_question_id,
            first_topic_questions
        ))
        assert first_question
        first_question_answers = first_question[0].get('answers', None)
        assert (len(first_question_answers) == first_topic_first_question_answers_count)

    def test_delete_questions(self):
        (first_topic_id, first_topic_questions,) = self._get_first_topic('id', 'questions')

        for question in first_topic_questions:
            question_id = question.get('id', None)
            assert question_id is not None

            response = self.client.delete(reverse('questions:questions-detail', args=[question_id]))
            assert (response.status_code == 200)

        (topic_questions,) = self._get_topic_by_id(first_topic_id, 'questions')
        assert (len(topic_questions) == 0)


@tag('api')
class UserApiFlowTestCase(AuthApiTestCase, DatabaseFilling, TopicHelper):

    user_id = 666

    def test_get_user_active_topics(self):
        user_active_topics_count = len(self._get_users_topics(self.user_id, is_active_not_passed=True))

        TopicFactory(
            start_date=(datetime.now() - timedelta(weeks=1)),
            finish_date=(datetime.now() - timedelta(days=1))
        )
        TopicFactory(
            start_date=(datetime.now() + timedelta(days=1)),
            finish_date=(datetime.now() + timedelta(weeks=1))
        )

        assert (user_active_topics_count == len(self._get_users_topics(self.user_id, is_active_not_passed=True)))

    @staticmethod
    def __get_question_and_answer_ids(question, is_reversed_answers=False) -> tuple:
        answers = question.get('answers')
        assert_list(answers)
        answer = (list(reversed(answers))[0] if is_reversed_answers else answers[0])
        assert isinstance(answer, dict)

        question_id = question.get('id', None)
        answer_id = answer.get('id', None)

        assert question_id is not None
        assert answer_id is not None

        return question_id, answer_id

    def __pass_question(self, question_id, answer_id):
        response = self.client.post(
            reverse('users-answers:users-answers-list'),
            data={
                'user_id': self.user_id,
                'question_id': question_id,
                'answer_id': answer_id,
            },
            format='json'
        )
        assert (response.status_code == 200)

    def test_pass_user_topic(self):
        user_active_topics = self._get_users_topics(self.user_id, is_active_not_passed=True)
        user_passed_topics_count = len(self._get_users_topics(self.user_id, is_active_not_passed=False))
        assert_list(user_active_topics)

        first_topic = user_active_topics[0]
        questions = first_topic.get('questions', None)
        assert_list(questions)

        for args in map(self.__get_question_and_answer_ids, questions):
            self.__pass_question(*args)

        question_id, answer_id = self.__get_question_and_answer_ids(questions[0], is_reversed_answers=True)
        self.__pass_question(question_id=question_id, answer_id=answer_id)

        user_passed_topics = self._get_users_topics(self.user_id, is_active_not_passed=False)
        assert_list(user_passed_topics)
        assert (user_passed_topics_count + 1 == len(user_passed_topics))

        questions = user_passed_topics[0].get('questions', None)
        assert_list(questions)
        passed_question = next(iter(filter(lambda question: question.get('id', None) == question_id, questions)))
        # TODO: check answer from passed question
