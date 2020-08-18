from datetime import datetime

from django.db.models import ProtectedError, Count, F, Q
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from common.enum import CustomEnum
from interview.apps.questions.models import Question
from interview.apps.topics.models import Topic, TopicSerializer
from interview.apps.users_answers.models import UserAnswer


class TopicViewSet(ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)

    __path_param_topic_id = Parameter(
        'id',
        in_=openapi.IN_PATH,
        description='Topic Id',
        type=openapi.TYPE_INTEGER
    )
    __response_item = {status.HTTP_200_OK: TopicSerializer(many=False)}
    __response_list = {status.HTTP_200_OK: TopicSerializer(many=True)}
    __response_400 = {status.HTTP_400_BAD_REQUEST: 'Received wrong topic object.'}
    __response_404 = {status.HTTP_404_NOT_FOUND: 'Topic not found.'}

    @swagger_auto_schema(
        responses={**__response_list}
    )
    def list(self, request):
        topics = Topic.objects.all()
        topics_serializer = TopicSerializer(topics, many=True)
        return Response(topics_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[__path_param_topic_id],
        responses={
            **__response_item,
            **__response_404,
        }
    )
    def retrieve(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        topic_serializer = TopicSerializer(topic)
        return Response(topic_serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=TopicSerializer,
        responses={
            **__response_item,
            **__response_400,
        }
    )
    def create(self, request):
        topic_serializer = TopicSerializer(data=request.data)
        if topic_serializer.is_valid():
            topic_serializer.save()
            return Response(topic_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(topic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[__path_param_topic_id],
        request_body=TopicSerializer,
        responses={
            **__response_item,
            **__response_400,
            **__response_404,
        }
    )
    def update(self, request, pk):
        topic = get_object_or_404(Topic, pk=pk)
        topic_serializer = TopicSerializer(topic, data=request.data, partial=True)
        if topic_serializer.is_valid():
            topic_serializer.save()
            return Response(topic_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(topic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[__path_param_topic_id],
        responses={
            status.HTTP_200_OK: 'Success delete topic object.',
            status.HTTP_400_BAD_REQUEST: 'Failed delete topic object.',
            **__response_404,
        }
    )
    def destroy(self, request, pk):
        try:
            topic = get_object_or_404(Topic, pk=pk)
            topic.delete()
            return Response(status=status.HTTP_200_OK)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserTopicType(CustomEnum):
    ACTIVE = 'active'
    PASSED = 'passed'


@swagger_auto_schema(
    method='GET',
    manual_parameters=[
        Parameter(
            'type',
            in_=openapi.IN_QUERY,
            description='Type',
            type=openapi.TYPE_STRING,
            enum=UserTopicType.values()
        ),
        Parameter(
            'user_id',
            in_=openapi.IN_QUERY,
            description='User Id',
            type=openapi.TYPE_INTEGER
        ),
    ],
    responses={
        status.HTTP_200_OK: TopicSerializer(many=True),
        status.HTTP_400_BAD_REQUEST: 'Received wrong parameters for filtering.'
    }
)
@api_view(['GET'])
def get_users_topics(request):
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

        # TODO: may be up performance [https://docs.djangoproject.com/en/3.1/ref/models/querysets/#in]
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

        users_answers = UserAnswer.objects.filter(
            user_id=user_id
        ).values_list(
            'question_id', 'answer_id'
        )
        answers_on_questions = {key: value for key, value in users_answers}

        topics_serializer = TopicSerializer(topics, many=True)
        topics = topics_serializer.data

        topics = __set_users_answers_to_questions(topics, answers_on_questions)

        return Response(topics, status=status.HTTP_200_OK)
    except AssertionError:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def __set_users_answers_to_questions(topics: list, answers_on_questions: dict) -> list:
    if len(answers_on_questions) > 0 and len(topics) > 0:
        for topic in topics:
            questions = topic.get('questions', [])
            for question in questions:
                answer_id = answers_on_questions.pop(question['id'], None)
                if answer_id is not None:
                    question['answer_id'] = answer_id
                if len(answers_on_questions) == 0:
                    return topics
    return topics
