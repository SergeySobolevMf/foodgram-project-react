from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserList, SignUp

app_name = 'foodgram'

router = DefaultRouter()


router.register('users', CustomUserList, basename='users')

urlpatterns = [
    path('api/signup/', SignUp.as_view(), name='signup'),
    path('api/', include(router.urls)),
]