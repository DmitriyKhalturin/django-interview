from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.topics.models import Topic, TopicSerializer


class TopicViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def list(self, request):
        topics = Topic.objects.all()
        topics_serializer = TopicSerializer(topics, many=True)
        return Response(topics_serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        topic_serializer = TopicSerializer(topic)
        return Response(topic_serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        topic_serializer = TopicSerializer(data=request.data)
        if topic_serializer.is_valid():
            topic_serializer.save()
            return Response(topic_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(topic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        topic_serializer = TopicSerializer(topic, data=request.data, partial=True)
        if topic_serializer.is_valid():
            topic_serializer.save()
            return Response(topic_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(topic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        try:
            topic = get_object_or_404(Topic, pk=pk)
            topic.delete()
            return Response(status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_users_topics(request):
    pass
