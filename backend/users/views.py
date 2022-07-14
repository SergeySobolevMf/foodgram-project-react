from urllib import response

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet
from rest_auth.views import LoginView
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser, Follow
from .pagination import LimitPageNumberPagination
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FollowSerializer)


class CustomUserList(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    pagination_class = PageNumberPagination

    # def get_permissions(self):
    #     if self.action in ['list', 'create', 'retrieve']:
    #         permission_classes = [AllowAny]
    #     return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return CustomUserCreateSerializer
        if self.action in ['subscribe', 'subscriptions']:
            return FollowSerializer
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

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        user = get_object_or_404(
            CustomUser,
            username=request.user.username
        )
        if serializer.is_valid():
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(
                serializer.data,
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class MyLoginView(LoginView):
    def get_response_serializer(self):
        return TokenSerializer


class Logout(APIView):
    def get(self, request, format=None):
        try:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return redirect('/api/auth/token/login/')


class FollowViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(
        methods=['post'], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response({
                'errors': 'Ошибка подписки, нельзя подписываться на себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Follow.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Ошибка подписки, вы уже подписаны на пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)

        follow = Follow.objects.create(user=user, author=author)
        serializer = FollowSerializer(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def del_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({
                'errors': 'Ошибка отписки, нельзя отписываться от самого себя'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, author=author)
        if not follow.exists():
            return Response({
                'errors': 'Ошибка отписки, вы уже отписались'
            }, status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
