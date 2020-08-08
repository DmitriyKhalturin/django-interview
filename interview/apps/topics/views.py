from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response


class TopicViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def list(self, request):
        pass

    def retrieve(self, request, pk):
        pass

    def create(self, request):
        pass

    def update(self, request, pk):
        pass

    def destroy(self, request, pk):
        pass


@api_view(['GET'])
def get_users_topics(request):
    pass
