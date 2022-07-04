import uuid

from rest_framework import status, viewsets
from django.core.mail import send_mail
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .models import Follow, CustomUser
from .serializers import (FollowSerializer,
                          CustomUserSerializer,
                          CumstomUserCreateSerializer)
from foodgram.settings import DEFAULT_FROM_EMAIL


class CustomUserList(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class SignUp(APIView):
    serializer_class = CumstomUserCreateSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = CumstomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )
        confirmation_code = uuid.uuid4()
        subject = 'Подтверждение регистрации'

        send_mail(
            subject=subject,
            message=(f'{subject} '
                     f'\nВаш confirmation_code: {confirmation_code}'),
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[email])
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowList(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer