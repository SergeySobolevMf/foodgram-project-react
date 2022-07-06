from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CustomUserList, MyLoginView, Logout

router = DefaultRouter()

router.register(r'users', CustomUserList, basename='users')

urlpatterns = [
    path('api/auth/token/login/', MyLoginView.as_view(), name="get_token"),
    path('api/auth/token/logout/', Logout.as_view(), name="delete_token"),
    path('api/', include(router.urls)),
]
