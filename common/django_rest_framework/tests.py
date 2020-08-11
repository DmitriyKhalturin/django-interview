from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient


class AuthAPITestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.client = APIClient()
        cls.user = User.objects.create_superuser('admin', 'admin@mail.com', 'passwd123')
        cls.token = Token.objects.create(user=cls.user)
        cls.storage = dict()

    def setUp(self) -> None:
        pass

    @staticmethod
    def authenticate(test_func):
        def func(instance):
            instance.client.force_authenticate(user=instance.user, token=instance.token)
            test_func(instance)
            instance.client.force_authenticate(user=None, token=None)

        return func
