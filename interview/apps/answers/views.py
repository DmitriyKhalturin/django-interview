from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ViewSet


class AnswerViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def update(self, request, pk):
        pass

    def destroy(self, request, pk):
        pass
