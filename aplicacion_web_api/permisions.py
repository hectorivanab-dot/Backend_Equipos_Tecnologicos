from rest_framework import permissions

class IsInstuctor(permissions.BasePermission):
    # Permitir el acceso unicamente a los usuarios con rol instructos
    def has_permissions(self, request, view):
        return bool(request.user and request.user.rol == 'instructor')