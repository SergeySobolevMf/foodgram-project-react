from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserList

router = DefaultRouter()

router.register('users', CustomUserList, basename='users')

urlpatterns = [
    path('api/auth/token/', include('rest_auth.urls')),
    path('api/', include(router.urls)),
]
