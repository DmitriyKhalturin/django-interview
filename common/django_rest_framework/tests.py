from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient


class AuthAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_superuser('admin', 'admin@mail.com', 'passwd123')
        self.token = Token.objects.create(user=self.user)

    def authenticate(self):
        self.client.force_authenticate(user=self.user, token=self.token)

    def unauthenticate(self):
        self.client.force_authenticate(user=None, token=None)
