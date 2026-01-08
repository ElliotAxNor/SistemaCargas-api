from rest_framework.permissions import BasePermission


class IsResponsableUnidad(BasePermission):
    """
    Permite acceso solo a usuarios con rol de Responsable de Unidad Académica.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol == 'RESP_UNIDAD'
        )


class IsResponsablePrograma(BasePermission):
    """
    Permite acceso solo a usuarios con rol de Responsable de Programa.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol == 'RESP_PROGRAMA'
        )
