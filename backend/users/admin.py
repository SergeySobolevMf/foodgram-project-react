from django.contrib import admin

from .models import CustomUser, Follow


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'email',
        'password')
    list_filter = ('email', 'username',)


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'author',
    )
    list_filter = ('user', 'author',)
    empty_value_display = '-----'


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
