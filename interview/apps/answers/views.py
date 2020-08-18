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

from interview.apps.answers.models import Answer, AnswerSerializer


class AnswerViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    __path_param_answer_id = Parameter(
        'id',
        in_=openapi.IN_PATH,
        description='Answer Id',
        type=openapi.TYPE_INTEGER
    )
    __response_item = {status.HTTP_200_OK: AnswerSerializer(many=False)}
    __response_400 = {status.HTTP_400_BAD_REQUEST: 'Received wrong question object.'}
    __response_404 = {status.HTTP_404_NOT_FOUND: 'Question not found.'}

    @swagger_auto_schema(
        manual_parameters=[__path_param_answer_id],
        request_body=AnswerSerializer,
        responses={
            **__response_item,
            **__response_400,
            **__response_404,
        }
    )
    def update(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        answer_serializer = AnswerSerializer(answer, data=request.data, partial=True)
        if answer_serializer.is_valid():
            answer_serializer.save()
            return Response(answer_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[__path_param_answer_id],
        responses={
            status.HTTP_200_OK: 'Success delete answer object.',
            status.HTTP_400_BAD_REQUEST: 'Failed delete answer object.',
            **__response_404,
        }
    )
    def destroy(self, request, pk):
        try:
            answer = get_object_or_404(Answer, pk=pk)
            answer.delete()
            return Response(status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
