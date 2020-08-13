from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import tag
from django.urls import reverse
from factory import Faker
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from interview.apps.questions.models import Question
from interview.tests.factories import TopicFactory, QuestionFactory, AnswerFactory


def authenticate(test_func):
    def func(instance):
        instance.client.force_authenticate(user=instance.user, token=instance.token)
        test_func(instance)
        instance.client.force_authenticate(user=None, token=None)

    return func


@tag('api')
class ApiFlowTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.client = cls.client_class()
        cls.user = User.objects.create_superuser('admin', 'admin@mail.com', 'passwd123')
        cls.token = Token.objects.create(user=cls.user)

    def setUp(self) -> None:
        super().setUp()

        for _ in range(3):
            topic = TopicFactory()
            for _ in range(3):
                question = QuestionFactory(topic=topic)
                for _ in range(3):
                    AnswerFactory(question=question)

    def __get_topics_count(self) -> int:
        """
        Get Topics count. ATTENTION! Before call this method, make authentication.
        :return: topics count.
        """
        __response = self.client.get(reverse('topics:topics-list'))
        assert (__response.status_code == 200)
        assert isinstance(__response.data, list)
        return len(__response.data)

    def __get_topics(self, filter_func, *keys) -> list:
        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)
        assert response.data

        topic = filter_func(response.data)
        assert isinstance(topic, dict)

        return list(map(lambda key: topic.get(key, None), *keys))

    def __get_first_topic(self, *keys) -> list:
        """
        Get first Topic. ATTENTION! Before call this method, make authentication.
        :param keys: list keys which will be returned.
        :return: values from topic object.
        """
        return self.__get_topics(
            lambda topics: topics[0],
            keys
        )

    def __get_topic_by_id(self, topic_id, *keys) -> list:
        """
        Get topic by id. ATTENTION! Before call this method, make authentication.
        :param keys: list keys which will be returned.
        :return: values from topic object.
        """
        return self.__get_topics(
            lambda topics: list(filter(lambda topic: topic.get('id', None) == topic_id, topics))[0],
            keys
        )

    # Default DB have 3 topics, 3 question with 3 answers for topic.

    @authenticate
    def test_create_topic(self):
        topics_count = self.__get_topics_count()

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

        assert (topics_count + 3 == self.__get_topics_count())

    @authenticate
    def test_get_and_clear_topics(self):
        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)

        for topic_id in [topic['id'] for topic in response.data]:
            response = self.client.delete(reverse('topics:topics-detail', args=[topic_id]))
            assert (response.status_code == 200)

        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)
        assert not response.data

    @authenticate
    def test_update_topic_field(self):
        (first_topic_id,) = self.__get_first_topic('id')

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

    @authenticate
    def test_catch_exception_update_topic_field(self):
        topics_count = self.__get_topics_count()
        (first_topic_id,) = self.__get_first_topic('id')

        response = self.client.put(
            reverse('topics:topics-detail', args=[first_topic_id]),
            data={
                'start_date': (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d'),
            },
            format='json'
        )
        assert (response.status_code == 400)
        assert (topics_count == self.__get_topics_count())

    @authenticate
    def test_delete_one_topic(self):
        topics_count = self.__get_topics_count()
        (first_topic_id,) = self.__get_first_topic('id')

        response = self.client.delete(reverse('topics:topics-detail', args=[first_topic_id]))
        assert (response.status_code == 200)
        assert (topics_count - 1 == self.__get_topics_count())

    @authenticate
    def test_create_question(self):
        (first_topic_id,) = self.__get_first_topic('id')

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
        assert isinstance(topic_questions, list)

        question_x = list(filter(lambda question: question.get('id', None) == question_x_id, topic_questions))
        assert question_x
        assert question_x[0].get('answers', None)

    @authenticate
    def test_catch_exception_create_questions(self):
        (first_topic_id, after_first_topic_questions,) = self.__get_first_topic('id', 'questions')

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
        (before_first_topic_questions,) = self.__get_topic_by_id(first_topic_id, 'questions')
        assert (len(after_first_topic_questions) == len(before_first_topic_questions))

    @authenticate
    def test_update_question(self):
        (first_topic_id, first_topic_questions,) = self.__get_first_topic('id', 'questions')
        assert isinstance(first_topic_questions, list)
        assert first_topic_questions
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

        (first_topic_questions,) = self.__get_topic_by_id(first_topic_id, 'questions')
        assert isinstance(first_topic_questions, list)

        first_question = list(filter(
            lambda question: question.get('id', None) == first_question_id,
            first_topic_questions
        ))
        assert first_question
        first_question_answers = first_question[0].get('answers', None)
        assert (len(first_question_answers) == first_topic_first_question_answers_count)

    @authenticate
    def test_delete_questions(self):
        (first_topic_id, first_topic_questions,) = self.__get_first_topic('id', 'questions')

        for question in first_topic_questions:
            question_id = question.get('id', None)
            assert question_id is not None

            response = self.client.delete(reverse('questions:questions-detail', args=[question_id]))
            assert (response.status_code == 200)

        (topic_questions,) = self.__get_topic_by_id(first_topic_id, 'questions')
        assert (len(topic_questions) == 0)

    # @authenticate
    # def test_010_create_user_answer(self):
    #     question_1_id = self.storage.get('question_1_id', None)
    #     answer_1_id = self.storage.get('answer_1_id', None)
    #     assert question_1_id is not None
    #     assert answer_1_id is not None
    #
    #     response = self.client.post(
    #         reverse('users-answers:users-answers-list'),
    #         data={
    #             'user_id': 666,
    #             'question_id': question_1_id,
    #             'answer_id': answer_1_id,
    #         },
    #         format='json'
    #     )
    #     assert (response.status_code == 200)
