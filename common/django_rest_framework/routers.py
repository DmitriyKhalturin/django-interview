from django.urls import path, include
from rest_framework.routers import DefaultRouter


def path_with_actions(prefix, viewset, basename):
    route = DefaultRouter()
    route.register(prefix, viewset, basename=basename)
    return path(r'', include(route.urls))
