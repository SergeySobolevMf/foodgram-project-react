from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import CustomUser, Follow
from .serializers import (CumstomUserCreateSerializer,
                          CustomUserSerializer,
                          FollowSerializer)


class CustomUserList(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CumstomUserCreateSerializer
        return CustomUserSerializer

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
    )
    def users_profile(self, request):
        user = get_object_or_404(
            CustomUser,
            username=request.user.username
        )
        serializer = self.get_serializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user = CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )
        user.set_password(serializer.validated_data.get('password'))
        user.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class FollowList(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
