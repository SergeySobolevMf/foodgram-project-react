from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)


class AdminOrReadOnly(BasePermission):
    def has_permission(self, request, obj):
        return (request.method in SAFE_METHODS or request.user.is_staff)


class AdminUserOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or (
                request.user == obj.author) or request.user.is_staff)


class AdminOrAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if (request.method in ['PATCH', 'DELETE'] and not
                request.user.is_anonymous):
            return (
                request.user == obj.author
                or request.user.is_superuser
            )
        return request.method in SAFE_METHODS

