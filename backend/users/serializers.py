from rest_framework import serializers
from rest_auth.models import TokenModel
from rest_auth.serializers import LoginSerializer

from .models import Follow, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email',)


class CumstomUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class CustomLoginSerializer(LoginSerializer):
    username = None


class MyTokenSerializer(serializers.ModelSerializer):

    access_token = serializers.SerializerMethodField()

    class Meta:
        model = TokenModel
        fields = ('access_token',)

    def get_access_token(self, obj):
        return obj.key


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'


