from django.db import models
from rest_framework import serializers

from interview.apps.questions.models import Question


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=512)
    question = models.ForeignKey(to=Question, related_name='answers', on_delete=models.CASCADE)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'text')


class CreateAnswerSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=512)
    question_id = serializers.IntegerField()

    def create(self, validated_data):
        return Answer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        pass
