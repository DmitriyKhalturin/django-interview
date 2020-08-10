from django.db import models
from rest_framework import serializers
from rest_framework.fields import empty

from interview.apps.topics.models import Topic


class Question(models.Model):
    # TODO: use TextChoices for Django > 3.0
    CUSTOM_OPTION = 'custom'
    ONE_OPTION = 'one'
    MULTIPLE_OPTION = 'multiple'

    TYPE_OPTION = (
        (CUSTOM_OPTION, 'Custom',),
        (ONE_OPTION, 'One',),
        (MULTIPLE_OPTION, 'Multiple',),
    )

    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=1024)
    type = models.CharField(max_length=8, choices=TYPE_OPTION)
    topic = models.ForeignKey(to=Topic, related_name='questions', on_delete=models.CASCADE)

    @classmethod
    def is_enumerate_type(cls, type_option):
        return type_option in {Question.ONE_OPTION, Question.MULTIPLE_OPTION}


class QuestionSerializer(serializers.ModelSerializer):
    from interview.apps.answers.models import AnswerSerializer

    answers = AnswerSerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = Question
        fields = ('id', 'text', 'type', 'answers')


class InsertQuestionSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=1024)
    type = serializers.CharField(max_length=8)
    answers = serializers.ListField(
        child=serializers.CharField(max_length=512),
        allow_empty=True
    )
    topic_id = serializers.IntegerField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        self.__answers = None

    def create(self, validated_data):
        self.__validate_answers(validated_data)
        question = Question.objects.create(**validated_data)
        self.__create_answers(question.id)
        return question

    def update(self, instance, validated_data):
        self.__validate_answers(validated_data)
        self.__delete_answers(instance.id)
        self.__create_answers(instance.id)
        instance.text = validated_data.get('text', instance.text)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        return instance

    def __validate_answers(self, validated_data):
        self.__answers = validated_data.pop('answers', [])

        count_answers = len(self.__answers)
        is_enumerate_type = Question.is_enumerate_type(validated_data['type'])

        if count_answers < 1 and is_enumerate_type:
            raise serializers.ValidationError('This \'type\' can\'t be used together an empty \'answers\'')
        elif count_answers > 0 and not is_enumerate_type:
            raise serializers.ValidationError('This \'type\' can\'t be used together a not empty \'answers\'')

    def __create_answers(self, question_id):
        from interview.apps.answers.models import Answer

        for text in self.__answers:
            Answer.objects.create(**{
                'text': text,
                'question_id': question_id,
            })

    @staticmethod
    def __delete_answers(question_id):
        from interview.apps.answers.models import Answer

        answers = Answer.objects.filter(question_id=question_id)
        for answer in answers:
            answer.delete()
