from django.db import models
from rest_framework import serializers

from common.transform import trunc_to8char
from interview.apps.questions.models import Question


class Answer(models.Model):

    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=512)
    question = models.ForeignKey(to=Question, related_name='answers', on_delete=models.CASCADE)

    class Meta:
        db_table = "answers"

    def __str__(self):
        return "%s [" \
               "id: %s, " \
               "text: %s, " \
               "question_id: %s, " \
               "]" %\
               (
                   self.__class__.__name__,
                   self.id,
                   trunc_to8char(self.text),
                   self.question_id,
               )


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'text',)


class CreateAnswerSerializer(serializers.Serializer):

    text = serializers.CharField(max_length=512)
    question_id = serializers.IntegerField()

    def create(self, validated_data):
        return Answer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        pass
