from django.db import models
from rest_framework import serializers

from interview.apps.questions.models import Question


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=512)
    question_id = models.ForeignKey(to=Question, on_delete=models.PROTECT)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
