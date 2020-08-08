from django.db import models
from rest_framework import serializers


class Topic(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256)
    start_date = models.DateField(blank=False, editable=False)
    finish_date = models.DateField(blank=False)
    description = models.CharField(max_length=512)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
