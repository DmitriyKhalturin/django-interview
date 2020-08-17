from datetime import datetime
from enum import Enum

from django.db.models import ProtectedError, Count, F, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from interview.apps.questions.models import Question
from interview.apps.topics.models import Topic, TopicSerializer


class TopicViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    @staticmethod
    def list(request):
        topics = Topic.objects.all()
        topics_serializer = TopicSerializer(topics, many=True)
        return Response(topics_serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def retrieve(request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        topic_serializer = TopicSerializer(topic)
        return Response(topic_serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def create(request):
        topic_serializer = TopicSerializer(data=request.data)
        if topic_serializer.is_valid():
            topic_serializer.save()
            return Response(topic_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(topic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def update(request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        topic_serializer = TopicSerializer(topic, data=request.data, partial=True)
        if topic_serializer.is_valid():
            topic_serializer.save()
            return Response(topic_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(topic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def destroy(request, pk):
        try:
            topic = get_object_or_404(Topic, pk=pk)
            topic.delete()
            return Response(status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserTopicType(Enum):
    ACTIVE = 'active'
    PASSED = 'passed'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@api_view(['GET'])
def get_users_topics(request):
    """
    Get Topics for user. Filtering by user_id, type.
    :param request: contain query params - user_id, type = [active, passed]
    :return: topics list.
    """
    try:
        user_topic_type = request.query_params.get('type')
        user_id = int(request.query_params.get('user_id'))

        assert UserTopicType.has_value(user_topic_type)
        assert isinstance(user_id, int)

        is_active_type = (user_topic_type == UserTopicType.ACTIVE.value)

        if is_active_type:
            topics_ids = Question.objects.values(
                'topic_id'
            ).annotate(
                total_questions=Count('id'),
                passed_questions=Count('id', filter=Q(answer__user_id=user_id))
            ).filter(
                total_questions__gt=F('passed_questions')
            ).values_list(
                'topic_id',
                flat=True
            )
        else:
            topics_ids = Question.objects.values(
                'topic_id'
            ).annotate(
                total_questions=Count('id'),
                passed_questions=Count('id', filter=Q(answer__user_id=user_id))
            ).filter(
                total_questions__exact=F('passed_questions')
            ).values_list(
                'topic_id',
                flat=True
            )

        # TODO: may be up performance [https://docs.djangoproject.com/en/2.2/ref/models/querysets/#in]
        if is_active_type:
            date = datetime.now().date()
            topics = Topic.objects.filter(
                Q(start_date__lte=date) & Q(finish_date__gte=date) &
                Q(id__in=topics_ids)
            )
        else:
            topics = Topic.objects.filter(
                id__in=topics_ids
            )

        topics_serializer = TopicSerializer(topics, many=True)
        return Response(topics_serializer.data, status=status.HTTP_200_OK)
    except AssertionError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
