from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserList, SignUp

app_name = 'foodgram'

router = DefaultRouter()


router.register('users', CustomUserList, basename='users')
router.register('signup', SignUp, basename='signup')

urlpatterns = [
    path('api/', include(router.urls)),
]