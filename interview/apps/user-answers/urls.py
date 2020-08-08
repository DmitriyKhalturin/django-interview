from common.drf.routers import path_with_actions
from .views import UserAnswersViewSet

app_name = 'user_answers'
urlpatterns = [
    path_with_actions(r'', UserAnswersViewSet, 'user_answers'),
]
