from django.db import models
from rest_framework import serializers

from interview.apps.answers.models import Answer
from interview.apps.questions.models import Question


class UserAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    question_id = models.ForeignKey(to=Question, on_delete=models.PROTECT)
    answer_id = models.ForeignKey(to=Answer, on_delete=models.PROTECT)


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
