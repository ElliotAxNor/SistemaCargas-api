"""
ViewSets para el módulo Académico.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Profesor, Materia
from .serializers import (
    ProfesorSerializer,
    ProfesorListSerializer,
    MateriaSerializer,
    MateriaListSerializer
)


class ProfesorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Profesores.

    list: Listar todos los profesores
    create: Crear un nuevo profesor
    retrieve: Obtener detalle de un profesor
    update: Actualizar un profesor
    partial_update: Actualizar parcialmente un profesor
    destroy: Eliminar un profesor
    """
    queryset = Profesor.objects.select_related('unidad_academica').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['unidad_academica']
    search_fields = ['nombre', 'email']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProfesorListSerializer
        return ProfesorSerializer

    def get_queryset(self):
        """
        Filtra profesores según la unidad del usuario.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Si es responsable de unidad, ver solo profesores de su unidad
        if hasattr(user, 'unidad_academica') and user.unidad_academica:
            queryset = queryset.filter(unidad_academica=user.unidad_academica)
        # Si es responsable de programa, ver profesores de la unidad de su programa
        elif hasattr(user, 'programa_academico') and user.programa_academico:
            queryset = queryset.filter(
                unidad_academica=user.programa_academico.unidad_academica
            )

        return queryset

    @action(detail=True, methods=['get'])
    def cargas(self, request, pk=None):
        """
        Obtiene todas las cargas de un profesor.
        GET /api/academico/profesores/{id}/cargas/
        """
        from apps.asignaciones.serializers import CargaListSerializer

        profesor = self.get_object()
        cargas = profesor.cargas.all()

        # Filtrar por periodo si se proporciona
        periodo_id = request.query_params.get('periodo')
        if periodo_id:
            cargas = cargas.filter(periodo_id=periodo_id)

        serializer = CargaListSerializer(cargas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def disponibilidad(self, request, pk=None):
        """
        Verifica la disponibilidad de un profesor en un periodo.
        GET /api/academico/profesores/{id}/disponibilidad/?periodo={periodo_id}

        Retorna:
        - Lista de cargas del profesor en el periodo
        - Bloques horarios ocupados
        """
        from apps.asignaciones.serializers import CargaSerializer
        from apps.asignaciones.models import Carga

        profesor = self.get_object()
        periodo_id = request.query_params.get('periodo')

        if not periodo_id:
            return Response(
                {'error': 'Debe proporcionar el parámetro periodo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cargas = Carga.objects.filter(
            profesor=profesor,
            periodo_id=periodo_id
        ).prefetch_related('bloques')

        serializer = CargaSerializer(cargas, many=True)

        return Response({
            'profesor': ProfesorSerializer(profesor).data,
            'total_cargas': cargas.count(),
            'cargas': serializer.data
        })


class MateriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Materias.

    list: Listar todas las materias
    create: Crear una nueva materia
    retrieve: Obtener detalle de una materia
    update: Actualizar una materia
    partial_update: Actualizar parcialmente una materia
    destroy: Eliminar una materia
    """
    queryset = Materia.objects.select_related('programa_academico').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['programa_academico', 'horas']
    search_fields = ['clave', 'nombre']
    ordering_fields = ['clave', 'nombre', 'horas', 'created_at']
    ordering = ['clave']

    def get_serializer_class(self):
        if self.action == 'list':
            return MateriaListSerializer
        return MateriaSerializer

    def get_queryset(self):
        """
        Filtra materias según el programa del usuario.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Si es responsable de unidad, ver todas las materias de su unidad
        if hasattr(user, 'unidad_academica') and user.unidad_academica:
            queryset = queryset.filter(
                programa_academico__unidad_academica=user.unidad_academica
            )
        # Si es responsable de programa, ver solo materias de su programa
        elif hasattr(user, 'programa_academico') and user.programa_academico:
            queryset = queryset.filter(programa_academico=user.programa_academico)

        return queryset

    @action(detail=True, methods=['get'])
    def cargas(self, request, pk=None):
        """
        Obtiene todas las cargas (secciones) de una materia.
        GET /api/academico/materias/{id}/cargas/
        """
        from apps.asignaciones.serializers import CargaListSerializer

        materia = self.get_object()
        cargas = materia.cargas.all()

        # Filtrar por periodo si se proporciona
        periodo_id = request.query_params.get('periodo')
        if periodo_id:
            cargas = cargas.filter(periodo_id=periodo_id)

        serializer = CargaListSerializer(cargas, many=True)
        return Response(serializer.data)
