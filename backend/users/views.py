from urllib import response
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_auth.views import LoginView
from django.core.exceptions import ObjectDoesNotExist


from .models import CustomUser, Follow
from .serializers import (CumstomUserCreateSerializer,
                          CumstomUserModifySerializer,
                          CustomUserSerializer,
                          FollowSerializer,
                          TokenSerializer)


class CustomUserList(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    pagination_class = PageNumberPagination

    # def get_permissions(self):
    #     if self.action in ['list', 'create', 'retrieve']:
    #         permission_classes = [AllowAny]
    #     return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return CumstomUserCreateSerializer
        if self.action == 'set_password':
            return CumstomUserModifySerializer
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


class FollowList(viewsets.ModelViewSet):

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
