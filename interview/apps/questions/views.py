from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.questions.models import Question, QuestionSerializer, InsertQuestionSerializer


class QuestionViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    __path_param_question_id = Parameter(
        'id',
        in_=openapi.IN_PATH,
        description='Question Id',
        type=openapi.TYPE_INTEGER
    )
    __response_item = {status.HTTP_200_OK: QuestionSerializer(many=False)}
    __response_list = {status.HTTP_200_OK: QuestionSerializer(many=True)}
    __response_400 = {status.HTTP_400_BAD_REQUEST: 'Received wrong question object.'}
    __response_404 = {status.HTTP_404_NOT_FOUND: 'Question not found.'}

    @swagger_auto_schema(
        request_body=InsertQuestionSerializer,
        responses={
            **__response_item,
            **__response_400,
        }
    )
    def create(self, request):
        question_serializer = InsertQuestionSerializer(data=request.data)
        if question_serializer.is_valid():
            question = question_serializer.save()
            return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)
        else:
            return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[__path_param_question_id],
        request_body=InsertQuestionSerializer,
        responses={
            **__response_item,
            **__response_400,
            **__response_404,
        }
    )
    def update(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        question_serializer = InsertQuestionSerializer(question, data=request.data, partial=True)
        if question_serializer.is_valid():
            question = question_serializer.save()
            return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)
        else:
            return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[__path_param_question_id],
        responses={
            status.HTTP_200_OK: 'Success delete question object.',
            status.HTTP_400_BAD_REQUEST: 'Failed delete question object.',
            **__response_404,
        }
    )
    def destroy(self, request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            question.delete()
            return Response(status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
