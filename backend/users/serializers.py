from rest_framework import serializers

from .models import Follow, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields = ('first_name', 'last_name', 'username', 'email',)


class CumstomUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email',)


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'


