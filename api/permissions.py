"""
==============================================================================
MÓDULO: API - PERMISOS PERSONALIZADOS (RBAC)
==============================================================================
Define las clases de permisos RBAC basadas en los atributos del modelo Usuario
inyectado en request.user.
==============================================================================
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizador(BasePermission):
    """
    Permiso para acciones exclusivas de usuarios con rol 'Organizador' o is_staff.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            getattr(request.user, 'rol', None) == 'Organizador'
            or request.user.is_staff
        )


class IsEspectador(BasePermission):
    """
    Permiso para acciones exclusivas de usuarios con rol 'Espectador'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return getattr(request.user, 'rol', None) == 'Espectador'


class IsOrganizadorOrReadOnly(BasePermission):
    """
    Permiso de lectura pública (SAFE_METHODS) y escritura restringida
    exclusivamente a usuarios con rol 'Organizador' o is_staff.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return (
            getattr(request.user, 'rol', None) == 'Organizador'
            or request.user.is_staff
        )