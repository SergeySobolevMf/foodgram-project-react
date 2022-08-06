from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import FollowViewSet

router = DefaultRouter()

router.register('users', FollowViewSet, basename='users')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
