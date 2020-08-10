from django.test import tag
from django.urls import include, path, reverse
from rest_framework.test import URLPatternsTestCase

from common.django_rest_framework.tests import AuthAPITestCase


@tag('api')
class TopicTestCase(AuthAPITestCase, URLPatternsTestCase):
    urlpatterns = [
        path(r'topics/', include('interview.apps.topics.urls')),
        path(r'questions/', include('interview.apps.questions.urls')),
        path(r'answers/', include('interview.apps.answers.urls')),
        path(r'user-answers/', include('interview.apps.user_answers.urls')),
    ]

    def test_1_topics(self):
        self.authenticate()

        response = self.client.post(
            reverse('topics:topics-list'),
            data={
                'title': 'Topic #1',
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

        response = self.client.post(
            reverse('topics:topics-list'),
            data={
                'title': 'Topic #2',
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

        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)
        assert (len(response.data) == 2)

        value_update_field = 'Updated field.'
        response = self.client.put(
            reverse('topics:topics-detail', args=[topic_1_id]),
            data={
                'description': value_update_field
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

        response = self.client.put(
            reverse('topics:topics-detail', args=[topic_1_id]),
            data={
                'start_date': '2020-08-11'
            },
            format='json'
        )
        assert (response.status_code == 400)

        response = self.client.delete(reverse('topics:topics-detail', args=[topic_2_id]))
        assert (response.status_code == 200)

        response = self.client.get(reverse('topics:topics-list'))
        assert (response.status_code == 200)
        assert isinstance(response.data, list)
        assert (len(response.data) == 1)

    # def test_2_(self):
    #     pass
    #
    # def test_3_(self):
    #     pass
    #
    # def test_4_(self):
    #     pass
    #
    # def test_5_(self):
    #     pass
