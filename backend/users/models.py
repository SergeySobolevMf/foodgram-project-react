from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER = 'User'
    ADMIN = 'Admin'
    USER_ROLE = ((USER, 'User'), (ADMIN, 'Admin'))
    username = models.CharField(max_length=150,
                                unique=True)
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        verbose_name='Роль',
        max_length=100,
        blank=True,
        choices=USER_ROLE,
        default=USER
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'username'],
                name='unique_auth'
            ),
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]

    def __str__(self):
        return f'{self.user} теперь подписчик {self.author}'