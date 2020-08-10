from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.answers.models import Answer, AnswerSerializer


class AnswerViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def update(self, request, pk):
        answer = get_object_or_404(Answer, pk=pk)
        answer_serializer = AnswerSerializer(answer, data=request.data, partial=True)
        if answer_serializer.is_valid():
            answer_serializer.save()
            return Response(answer_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            answer = get_object_or_404(Answer, pk=pk)
            answer.delete()
            return Response(status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
