from rest_framework import serializers

from .models import Follow, CustomUser


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'


class CumstomUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'login', 'email',)

    def save(self):
        account = CustomUser(
            login=self.validated_data['login'],
            email=self.validated_data['email']
        )
        password = self.validated_data['password']
        account.set_password(password)
        account.save()
        return account