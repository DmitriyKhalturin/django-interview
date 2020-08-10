from common.django_rest_framework.routers import path_with_actions
from .views import AnswerViewSet

app_name = 'answers'
urlpatterns = [
    path_with_actions(r'', AnswerViewSet, 'answers'),
]
