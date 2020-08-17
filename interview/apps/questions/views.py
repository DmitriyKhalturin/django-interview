from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.questions.models import Question, QuestionSerializer, InsertQuestionSerializer


class QuestionViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    @staticmethod
    def create(request):
        question_serializer = InsertQuestionSerializer(data=request.data)
        if question_serializer.is_valid():
            question = question_serializer.save()
            return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)
        else:
            return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update(request, pk):
        question = get_object_or_404(Question, pk=pk)
        question_serializer = InsertQuestionSerializer(question, data=request.data, partial=True)
        if question_serializer.is_valid():
            question = question_serializer.save()
            return Response(QuestionSerializer(question).data, status=status.HTTP_200_OK)
        else:
            return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def destroy(request, pk):
        try:
            question = get_object_or_404(Question, pk=pk)
            question.delete()
            return Response(status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
