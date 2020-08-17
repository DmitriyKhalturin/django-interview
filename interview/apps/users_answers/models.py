from django.db import models
from rest_framework import serializers

from interview.apps.answers.models import Answer, AnswerSerializer
from interview.apps.questions.models import Question, QuestionSerializer


class UserAnswer(models.Model):

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(db_index=True)
    question = models.ForeignKey(to=Question, related_name='answer', on_delete=models.CASCADE)
    answer = models.ForeignKey(to=Answer, on_delete=models.CASCADE)

    class Meta:
        db_table = "users_answers"

    def __str__(self):
        return "%s [" \
               "id: %s, " \
               "user_id: %s, " \
               "question_id: %s, " \
               "answer_id: %s, " \
               "]" %\
               (
                   self.__class__.__name__,
                   self.id,
                   self.user_id,
                   self.question_id,
                   self.answer_id,
               )


class UserAnswerSerializer(serializers.ModelSerializer):

    question = QuestionSerializer(many=False, read_only=True, allow_null=False)
    answer = AnswerSerializer(many=False, read_only=True, allow_null=False)

    class Meta:
        model = UserAnswer
        fields = ('user_id', 'question', 'answer',)


class CreateUserAnswerSerializer(serializers.Serializer):

    user_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()

    def create(self, validated_data):
        return UserAnswer.objects.create(**validated_data)

    def update(self, instance, validated_data):
        pass


class UpdateUserAnswerSerializer(serializers.Serializer):

    answer_id = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        instance.answer_id = validated_data.get('answer_id', instance.answer_id)
        instance.save()
        return instance
