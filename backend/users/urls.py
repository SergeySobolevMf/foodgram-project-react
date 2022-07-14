from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import FollowViewSet

router = DefaultRouter()

router.register('users', FollowViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]