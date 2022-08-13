from rest_framework.permissions import (SAFE_METHODS,
                                        BasePermission,)


class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if request.user == obj.author:
            return True
        return request.method in SAFE_METHODS or request.user.is_superuser
