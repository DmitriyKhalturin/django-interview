from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.users_answers.models import UserAnswerSerializer, CreateUserAnswerSerializer


class UserAnswerViewSet(ViewSet):
    def create(self, request):
        user_answer_serializer = CreateUserAnswerSerializer(data=request.data)
        if user_answer_serializer.is_valid():
            user_answer = user_answer_serializer.save()
            return Response(UserAnswerSerializer(user_answer).data, status=status.HTTP_200_OK)
        else:
            return Response(user_answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
