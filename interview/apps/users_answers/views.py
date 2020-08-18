from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.users_answers.models import UserAnswer, UserAnswerSerializer, CreateUserAnswerSerializer, \
    UpdateUserAnswerSerializer


class UserAnswerViewSet(ViewSet):

    @swagger_auto_schema(
        request_body=CreateUserAnswerSerializer,
        responses={
            status.HTTP_200_OK: UserAnswerSerializer(many=False),
            status.HTTP_400_BAD_REQUEST: 'Received wrong user answer object.'
        }
    )
    def create(self, request):
        user_answer_serializer = CreateUserAnswerSerializer(data=request.data)
        if user_answer_serializer.is_valid():
            users_answers = UserAnswer.objects.filter(
                Q(user_id=user_answer_serializer.validated_data['user_id']) &
                Q(question_id=user_answer_serializer.validated_data['question_id'])
            )

            user_answer = next(iter(users_answers), None)
            if user_answer is not None:
                answer_id = user_answer_serializer.validated_data['answer_id']
                user_answer_serializer = UpdateUserAnswerSerializer(
                    user_answer,
                    {'answer_id': answer_id},
                    partial=True
                )
                if not user_answer_serializer.is_valid():
                    return Response(user_answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user_answer = user_answer_serializer.save()
            return Response(UserAnswerSerializer(user_answer).data, status=status.HTTP_200_OK)
        else:
            return Response(user_answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
