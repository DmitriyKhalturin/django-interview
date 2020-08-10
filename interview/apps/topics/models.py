from django.db import models
from rest_framework import serializers


class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    start_date = models.DateField(blank=False)
    finish_date = models.DateField(blank=False)
    description = models.CharField(max_length=512)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'title', 'start_date', 'finish_date', 'description')

    def update(self, instance, validated_data):
        if validated_data.get('start_date', None) is not None:
            raise serializers.ValidationError('Field \'start_date\' can\'t be modified')
        else:
            return super().update(instance, validated_data)
