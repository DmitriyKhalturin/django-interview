from django.db import models
from rest_framework import serializers

from common.transform import trunc_to8char


class Topic(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    start_date = models.DateField(blank=False)
    finish_date = models.DateField(blank=False)
    description = models.CharField(max_length=512)

    class Meta:
        db_table = "topics"

    def __str__(self):
        return "%s [" \
               "id: %s, " \
               "title: %s, " \
               "start_data: %s, " \
               "finish_date: %s, " \
               "description: %s, " \
               "]" %\
               (
                   self.__class__.__name__,
                   self.id,
                   trunc_to8char(self.title),
                   self.start_date,
                   self.finish_date,
                   trunc_to8char(self.description),
               )


class TopicSerializer(serializers.ModelSerializer):
    from interview.apps.questions.models import QuestionSerializer

    questions = QuestionSerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = Topic
        fields = ('id', 'title', 'start_date', 'finish_date', 'description', 'questions',)

    def update(self, instance, validated_data):
        if validated_data.get('start_date', None) is not None:
            raise serializers.ValidationError('Field \'start_date\' can\'t be modified.')
        else:
            return super().update(instance, validated_data)
