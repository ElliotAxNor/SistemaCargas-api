"""
ViewSets para el módulo Asignaciones.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Periodo, Carga, BloqueHorario
from .serializers import (
    PeriodoSerializer,
    PeriodoListSerializer,
    CargaSerializer,
    CargaDetailSerializer,
    CargaListSerializer,
    CargaCreateUpdateSerializer,
    BloqueHorarioSerializer
)
from .services import ValidadorConflictos, ValidadorHoras, PeriodoService
from common.permissions import IsResponsableUnidad, IsResponsablePrograma


class PeriodoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Periodos Académicos.

    list: Listar todos los periodos
    create: Crear un nuevo periodo
    retrieve: Obtener detalle de un periodo
    update: Actualizar un periodo
    partial_update: Actualizar parcialmente un periodo
    destroy: Eliminar un periodo
    """
    queryset = Periodo.objects.select_related('unidad_academica').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['unidad_academica', 'finalizado']
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['-nombre']

    def get_serializer_class(self):
        if self.action == 'list':
            return PeriodoListSerializer
        return PeriodoSerializer

    def get_queryset(self):
        """
        Filtra periodos según la unidad del usuario.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Si es responsable de unidad, ver periodos de su unidad
        if hasattr(user, 'unidad_academica') and user.unidad_academica:
            queryset = queryset.filter(unidad_academica=user.unidad_academica)
        # Si es responsable de programa, ver periodos de la unidad de su programa
        elif hasattr(user, 'programa_academico') and user.programa_academico:
            queryset = queryset.filter(
                unidad_academica=user.programa_academico.unidad_academica
            )

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsResponsableUnidad])
    def finalizar(self, request, pk=None):
        """
        Finaliza un periodo académico.
        Solo puede hacerlo el responsable de unidad.
        POST /api/asignaciones/periodos/{id}/finalizar/
        """
        periodo = self.get_object()
        resultado = PeriodoService.finalizar_periodo(periodo)

        if resultado['success']:
            return Response({
                'mensaje': resultado['mensaje'],
                'periodo': PeriodoSerializer(periodo).data
            })
        else:
            # Serializar cargas problemáticas si existen
            response_data = {
                'success': resultado['success'],
                'mensaje': resultado['mensaje']
            }

            if 'cargas_problematicas' in resultado:
                cargas_prob = resultado['cargas_problematicas']
                response_data['cargas_problematicas'] = {
                    'pendientes': CargaListSerializer(cargas_prob['pendientes'], many=True).data
                }

            return Response(
                response_data,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """
        Obtiene estadísticas del periodo.
        GET /api/asignaciones/periodos/{id}/estadisticas/
        """
        periodo = self.get_object()
        estadisticas = PeriodoService.obtener_estadisticas_periodo(periodo)
        return Response(estadisticas)

    @action(detail=True, methods=['get'])
    def cargas_problematicas(self, request, pk=None):
        """
        Obtiene las cargas pendientes (incompletas) del periodo.
        GET /api/asignaciones/periodos/{id}/cargas_problematicas/
        """
        periodo = self.get_object()
        cargas_problematicas = PeriodoService.obtener_cargas_problematicas(periodo)

        return Response({
            'total_pendientes': len(cargas_problematicas['pendientes']),
            'pendientes': CargaListSerializer(cargas_problematicas['pendientes'], many=True).data
        })


class CargaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Cargas.

    list: Listar todas las cargas
    create: Crear una nueva carga (con validación automática)
    retrieve: Obtener detalle de una carga
    update: Actualizar una carga (con validación automática)
    partial_update: Actualizar parcialmente una carga
    destroy: Eliminar una carga
    """
    queryset = Carga.objects.select_related(
        'programa_academico',
        'materia',
        'profesor',
        'periodo'
    ).prefetch_related('bloques').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['programa_academico', 'profesor', 'periodo', 'estado']
    search_fields = ['materia__clave', 'materia__nombre', 'profesor__nombre']
    ordering_fields = ['created_at', 'estado']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            # Usar serializer con objetos completos anidados para lectura
            return CargaDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CargaCreateUpdateSerializer
        return CargaDetailSerializer

    def get_queryset(self):
        """
        Filtra cargas según el programa/unidad del usuario.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Si es responsable de unidad, ver todas las cargas de su unidad
        if hasattr(user, 'unidad_academica') and user.unidad_academica:
            queryset = queryset.filter(
                programa_academico__unidad_academica=user.unidad_academica
            )
        # Si es responsable de programa, ver solo cargas de su programa
        elif hasattr(user, 'programa_academico') and user.programa_academico:
            queryset = queryset.filter(programa_academico=user.programa_academico)

        return queryset

    @action(detail=False, methods=['post'])
    def validar_disponibilidad(self, request):
        """
        Valida si un profesor está disponible antes de crear la carga.
        POST /api/asignaciones/cargas/validar_disponibilidad/

        Body:
        {
            "profesor_id": 1,
            "periodo_id": 1,
            "bloques": [
                {"dia": "LUN", "hora_inicio": "08:00", "hora_fin": "10:00"}
            ]
        }
        """
        from apps.academico.models import Profesor

        profesor_id = request.data.get('profesor_id')
        periodo_id = request.data.get('periodo_id')
        bloques_data = request.data.get('bloques', [])

        if not all([profesor_id, periodo_id, bloques_data]):
            return Response(
                {'error': 'Debe proporcionar profesor_id, periodo_id y bloques.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profesor = Profesor.objects.get(id=profesor_id)
            periodo = Periodo.objects.get(id=periodo_id)
        except (Profesor.DoesNotExist, Periodo.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

        # Crear instancias temporales de bloques
        from datetime import datetime
        bloques_temp = []
        for bloque_data in bloques_data:
            # Convertir strings de tiempo a datetime.time
            hora_inicio = bloque_data['hora_inicio']
            hora_fin = bloque_data['hora_fin']

            # Si son strings, convertir a time objects
            if isinstance(hora_inicio, str):
                hora_inicio = datetime.strptime(hora_inicio, '%H:%M:%S').time()
            if isinstance(hora_fin, str):
                hora_fin = datetime.strptime(hora_fin, '%H:%M:%S').time()

            bloques_temp.append(BloqueHorario(
                dia=bloque_data['dia'],
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            ))

        # Validar disponibilidad
        conflicto = ValidadorConflictos.validar_disponibilidad_profesor(
            profesor=profesor,
            periodo=periodo,
            bloques=bloques_temp
        )

        if conflicto:
            # Extraer valores serializables del conflicto
            carga_id = int(conflicto['carga_conflictiva'].id)
            programa = str(conflicto['programa'])
            materia = str(conflicto['materia'])
            materia_clave = str(conflicto['materia_clave'])

            return Response({
                'disponible': False,
                'mensaje': f"El profesor ya tiene asignada la materia {materia} del programa {programa}",
                'conflicto': {
                    'carga_id': carga_id,
                    'programa': programa,
                    'materia': materia,
                    'materia_clave': materia_clave
                }
            }, status=status.HTTP_409_CONFLICT)

        return Response({
            'disponible': True,
            'mensaje': 'El profesor está disponible en los horarios especificados.'
        })

    @action(detail=True, methods=['get'])
    def validar(self, request, pk=None):
        """
        Valida una carga existente (conflictos y horas).
        GET /api/asignaciones/cargas/{id}/validar/
        """
        carga = self.get_object()

        # Validar horas
        horas_validas = ValidadorHoras.validar_horas_carga(carga)
        total_horas_bloques = ValidadorHoras.calcular_total_horas_bloques(carga)

        # Validar conflictos
        conflicto = ValidadorConflictos.detectar_conflicto_carga(carga)

        resultado = {
            'carga_id': carga.id,
            'estado_actual': carga.estado,
            'validaciones': {
                'horas': {
                    'valida': horas_validas,
                    'horas_materia': carga.materia.horas,
                    'horas_bloques': total_horas_bloques
                },
                'conflictos': {
                    'tiene_conflicto': conflicto is not None,
                    'detalle': conflicto if conflicto else None
                }
            }
        }

        return Response(resultado)

    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """
        Agrupa las cargas por estado.
        GET /api/asignaciones/cargas/por_estado/?periodo={periodo_id}
        """
        queryset = self.get_queryset()

        # Filtrar por periodo si se proporciona
        periodo_id = request.query_params.get('periodo')
        if periodo_id:
            queryset = queryset.filter(periodo_id=periodo_id)

        # Agrupar por estado
        correctas = queryset.filter(estado=Carga.Estado.CORRECTA).count()
        pendientes = queryset.filter(estado=Carga.Estado.PENDIENTE).count()

        return Response({
            'total': queryset.count(),
            'correctas': correctas,
            'pendientes': pendientes
        })


class BloqueHorarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Bloques Horarios.
    Los bloques se gestionan a través de las cargas.

    list: Listar todos los bloques horarios
    retrieve: Obtener detalle de un bloque horario
    """
    queryset = BloqueHorario.objects.select_related('carga').all()
    serializer_class = BloqueHorarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['carga', 'dia']
    ordering_fields = ['dia', 'hora_inicio']
    ordering = ['dia', 'hora_inicio']

    def get_queryset(self):
        """
        Filtra bloques según el acceso del usuario.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Si es responsable de unidad, ver todos los bloques de su unidad
        if hasattr(user, 'unidad_academica') and user.unidad_academica:
            queryset = queryset.filter(
                carga__programa_academico__unidad_academica=user.unidad_academica
            )
        # Si es responsable de programa, ver solo bloques de su programa
        elif hasattr(user, 'programa_academico') and user.programa_academico:
            queryset = queryset.filter(
                carga__programa_academico=user.programa_academico
            )

        return queryset
