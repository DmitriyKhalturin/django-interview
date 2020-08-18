"""interview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken import views
from rest_framework.permissions import AllowAny

from interview.apps.topics.views import get_users_topics

schema_view = get_schema_view(
    openapi.Info(
        title="Interview API",
        default_version='v1'
    ),
    public=True,
    authentication_classes=(TokenAuthentication,),
    permission_classes=(AllowAny,),
)
urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'auth-token/', views.obtain_auth_token),
    path(r'topics/', include('interview.apps.topics.urls')),
    path(r'questions/', include('interview.apps.questions.urls')),
    path(r'users-topics/', get_users_topics, name='users-topics-list'),
    path(r'users-answers/', include('interview.apps.users_answers.urls')),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
