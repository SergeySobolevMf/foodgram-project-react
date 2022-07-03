from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Follow, CustomUser
from .serializers import FollowSerializer, CumstomUserCreateSerializer


class CustomUserList(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CumstomUserCreateSerializer
    


class FollowList(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer