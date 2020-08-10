from django.db import models
from rest_framework import serializers

from interview.apps.topics.models import Topic


class Question(models.Model):

    CUSTOM_OPTION = 'CUSTOM'
    ONE_OPTION = 'ONE'
    MULTIPLE_OPTION = 'MULTIPLE'

    TYPE_OPTION = (
        (CUSTOM_OPTION, 'custom',),
        (ONE_OPTION, 'one',),
        (MULTIPLE_OPTION, 'multiple',),
    )

    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=1024)
    type = models.CharField(max_length=8, choices=TYPE_OPTION)
    topic_id = models.ForeignKey(to=Topic, on_delete=models.PROTECT)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
