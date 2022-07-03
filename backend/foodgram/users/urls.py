from django.urls import include, path
from rest_framework.routers import DefaultRouter

from backend.foodgram.users.views import CustomUserList

app_name = 'foodgram'

router = DefaultRouter()


router.register('users', CustomUserList, basename='users')

urlpatterns = [
    path('api/', include(router.urls)),
]