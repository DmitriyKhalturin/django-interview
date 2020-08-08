from rest_framework.viewsets import ViewSet
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser


class QuestionViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def create(self, request):
        pass

    def update(self, request, pk):
        pass

    def destroy(self, request, pk):
        pass
