from django.urls import path

from common.django_rest_framework.routers import path_with_actions
from . import views
from .views import TopicViewSet

app_name = 'topics'
urlpatterns = [
    path(r'users/', views.get_users_topics, name='users-topics-list'),
    path_with_actions(r'', TopicViewSet, 'topics'),
]
