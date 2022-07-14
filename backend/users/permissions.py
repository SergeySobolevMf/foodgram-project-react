from rest_framework import permissions

from .models import CustomUser


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.role == CustomUser.ADMIN)

