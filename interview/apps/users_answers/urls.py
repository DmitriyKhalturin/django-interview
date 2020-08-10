from common.django_rest_framework.routers import path_with_actions
from .views import UserAnswerViewSet

app_name = 'users-answers'
urlpatterns = [
    path_with_actions(r'', UserAnswerViewSet, 'users-answers'),
]
