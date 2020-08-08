from common.drf.routers import path_with_actions
from .views import QuestionViewSet

app_name = 'questions'
urlpatterns = [
    path_with_actions(r'', QuestionViewSet, 'questions'),
]
