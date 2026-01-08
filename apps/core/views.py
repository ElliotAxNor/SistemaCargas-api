"""
ViewSets para el módulo Core.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import UnidadAcademica, ProgramaAcademico, Usuario
from .serializers import (
    UnidadAcademicaSerializer,
    ProgramaAcademicoSerializer,
    ProgramaAcademicoListSerializer,
    UsuarioSerializer,
    UsuarioCreateUpdateSerializer,
    UsuarioListSerializer
)
from common.permissions import IsResponsableUnidad


class UnidadAcademicaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Unidades Académicas.

    list: Listar todas las unidades académicas
    create: Crear una nueva unidad académica
    retrieve: Obtener detalle de una unidad académica
    update: Actualizar una unidad académica
    partial_update: Actualizar parcialmente una unidad académica
    destroy: Eliminar una unidad académica
    """
    queryset = UnidadAcademica.objects.all()
    serializer_class = UnidadAcademicaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']

    @action(detail=True, methods=['get'])
    def programas(self, request, pk=None):
        """
        Obtiene todos los programas académicos de una unidad.
        GET /api/core/unidades-academicas/{id}/programas/
        """
        unidad = self.get_object()
        programas = unidad.programas.all()
        serializer = ProgramaAcademicoListSerializer(programas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def profesores(self, request, pk=None):
        """
        Obtiene todos los profesores de una unidad.
        GET /api/core/unidades-academicas/{id}/profesores/
        """
        from apps.academico.serializers import ProfesorListSerializer

        unidad = self.get_object()
        profesores = unidad.profesores.all()
        serializer = ProfesorListSerializer(profesores, many=True)
        return Response(serializer.data)


class ProgramaAcademicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Programas Académicos.

    list: Listar todos los programas académicos
    create: Crear un nuevo programa académico
    retrieve: Obtener detalle de un programa académico
    update: Actualizar un programa académico
    partial_update: Actualizar parcialmente un programa académico
    destroy: Eliminar un programa académico
    """
    queryset = ProgramaAcademico.objects.select_related('unidad_academica').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['unidad_academica']
    search_fields = ['nombre', 'unidad_academica__nombre']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProgramaAcademicoListSerializer
        return ProgramaAcademicoSerializer

    @action(detail=True, methods=['get'])
    def materias(self, request, pk=None):
        """
        Obtiene todas las materias de un programa.
        GET /api/core/programas-academicos/{id}/materias/
        """
        from apps.academico.serializers import MateriaListSerializer

        programa = self.get_object()
        materias = programa.materias.all()
        serializer = MateriaListSerializer(materias, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def cargas(self, request, pk=None):
        """
        Obtiene todas las cargas de un programa.
        GET /api/core/programas-academicos/{id}/cargas/
        """
        from apps.asignaciones.serializers import CargaListSerializer

        programa = self.get_object()
        cargas = programa.cargas.all()

        # Filtrar por periodo si se proporciona
        periodo_id = request.query_params.get('periodo')
        if periodo_id:
            cargas = cargas.filter(periodo_id=periodo_id)

        serializer = CargaListSerializer(cargas, many=True)
        return Response(serializer.data)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Usuarios.

    Solo los responsables de unidad pueden gestionar usuarios.

    list: Listar todos los usuarios
    create: Crear un nuevo usuario
    retrieve: Obtener detalle de un usuario
    update: Actualizar un usuario
    partial_update: Actualizar parcialmente un usuario
    destroy: Eliminar un usuario
    """
    queryset = Usuario.objects.select_related(
        'unidad_academica',
        'programa_academico'
    ).all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['rol', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']
    ordering = ['username']

    def get_permissions(self):
        """
        Solo los responsables de unidad pueden crear/editar/eliminar usuarios.
        Cualquier usuario autenticado puede ver su propio perfil.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsResponsableUnidad()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateUpdateSerializer
        return UsuarioSerializer

    def get_queryset(self):
        """
        Los responsables de unidad ven todos los usuarios de su unidad.
        Los responsables de programa solo ven su propio perfil.
        """
        user = self.request.user

        if user.rol == Usuario.Rol.RESP_UNIDAD:
            # Ver todos los usuarios de su unidad
            return Usuario.objects.filter(
                unidad_academica=user.unidad_academica
            ) | Usuario.objects.filter(
                programa_academico__unidad_academica=user.unidad_academica
            )
        else:
            # Solo ver su propio perfil
            return Usuario.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Obtiene el perfil del usuario autenticado.
        GET /api/core/usuarios/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        """
        Permite cambiar la contraseña de un usuario.
        POST /api/core/usuarios/{id}/cambiar_password/
        {
            "password_actual": "...",
            "password_nuevo": "..."
        }
        """
        usuario = self.get_object()
        password_actual = request.data.get('password_actual')
        password_nuevo = request.data.get('password_nuevo')

        # Verificar que el usuario solo puede cambiar su propia contraseña
        # o que sea responsable de unidad
        if usuario != request.user and request.user.rol != Usuario.Rol.RESP_UNIDAD:
            return Response(
                {'error': 'No tienes permiso para cambiar esta contraseña.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Si no es responsable de unidad, verificar contraseña actual
        if request.user.rol != Usuario.Rol.RESP_UNIDAD:
            if not usuario.check_password(password_actual):
                return Response(
                    {'error': 'La contraseña actual es incorrecta.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Cambiar contraseña
        usuario.set_password(password_nuevo)
        usuario.save()

        return Response({'mensaje': 'Contraseña actualizada exitosamente.'})
