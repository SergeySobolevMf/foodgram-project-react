from pkg_resources import require
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


class CumstomUserModifySerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True, max_length=200)
    current_password = serializers.CharField(source='password')

    class Meta:
        model = CustomUser
        fields = ('new_password', 'current_password',)


class CustomLoginSerializer(LoginSerializer):
    username = None


class TokenSerializer(serializers.ModelSerializer):

    access_token = serializers.CharField(source='key')

    class Meta:
        model = TokenModel
        fields = ('access_token',)

    def get_access_token(self, obj):
        return obj.key


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


