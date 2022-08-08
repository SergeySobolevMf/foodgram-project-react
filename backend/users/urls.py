from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import UserViewSet

router = SimpleRouter()

router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
]
