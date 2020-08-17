from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.users_answers.models import UserAnswer, UserAnswerSerializer, CreateUserAnswerSerializer, \
    UpdateUserAnswerSerializer


class UserAnswerViewSet(ViewSet):

    @staticmethod
    def __get_query_param(data: dict, name: str):
        param = data.get(name, None)
        assert param is not None
        return param

    @staticmethod
    def create(request):
        users_answers = UserAnswer.objects.filter(
            Q(user_id=UserAnswerViewSet.__get_query_param(request.data, 'user_id')) &
            Q(question_id=UserAnswerViewSet.__get_query_param(request.data, 'question_id'))
        )
        user_answer = next(iter(users_answers), None)

        if user_answer is not None:
            answer_id = UserAnswerViewSet.__get_query_param(request.data, 'answer_id')
            user_answer_serializer = UpdateUserAnswerSerializer(
                user_answer,
                {'answer_id': answer_id},
                partial=True
            )
        else:
            user_answer_serializer = CreateUserAnswerSerializer(data=request.data)

        if user_answer_serializer.is_valid():
            user_answer = user_answer_serializer.save()
            return Response(UserAnswerSerializer(user_answer).data, status=status.HTTP_200_OK)
        else:
            return Response(user_answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
