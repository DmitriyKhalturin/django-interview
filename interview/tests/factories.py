from datetime import datetime, timedelta

import factory
from factory.django import DjangoModelFactory

from interview.apps.answers.models import Answer
from interview.apps.questions.models import Question
from interview.apps.topics.models import Topic


class TopicFactory(DjangoModelFactory):
    class Meta:
        model = Topic

    title = factory.Faker('text', max_nb_chars=256)
    start_date = factory.LazyFunction(datetime.now)
    finish_date = factory.LazyFunction(lambda: datetime.now() + timedelta(weeks=1))
    description = factory.Faker('text', max_nb_chars=512)


class QuestionFactory(DjangoModelFactory):
    class Meta:
        model = Question

    text = factory.Faker('text', max_nb_chars=1024)
    type = factory.Iterator((
        # Question.CUSTOM_OPTION, # remove this type, as this question can't have answers
        Question.ONE_OPTION,
        Question.MULTIPLE_OPTION,
    ))
    topic = factory.SubFactory(TopicFactory)


class AnswerFactory(DjangoModelFactory):
    class Meta:
        model = Answer

    text = factory.Faker('text', max_nb_chars=512)
    question = factory.SubFactory(QuestionFactory)
