from django.urls import path

from common.drf.routers import path_with_actions
from . import views
from .views import TopicViewSet

app_name = 'topics'
urlpatterns = [
    path(r'users/', views.get_users_topics, name='users_topics'),
    path_with_actions(r'', TopicViewSet, 'topics'),
]
