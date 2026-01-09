"""
Serializers para el módulo Asignaciones.
Integra validaciones de negocio usando los services.
"""

from rest_framework import serializers
from .models import Periodo, Carga, BloqueHorario
from .services import ValidadorConflictos, ValidadorHoras, PeriodoService
from common.exceptions import ConflictoHorarioException, HorasInvalidasException
from apps.core.serializers import ProgramaAcademicoSerializer
from apps.academico.serializers import MateriaSerializer, ProfesorSerializer


class PeriodoSerializer(serializers.ModelSerializer):
    """
    Serializer para Periodo.
    """
    unidad_academica_nombre = serializers.CharField(
        source='unidad_academica.nombre',
        read_only=True
    )
    puede_finalizar = serializers.SerializerMethodField()
    estadisticas = serializers.SerializerMethodField()

    class Meta:
        model = Periodo
        fields = [
            'id',
            'unidad_academica',
            'unidad_academica_nombre',
            'nombre',
            'finalizado',
            'puede_finalizar',
            'estadisticas',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'finalizado']

    def get_puede_finalizar(self, obj):
        """Verifica si el periodo puede ser finalizado (usando service)."""
        return PeriodoService.puede_finalizar(obj)

    def get_estadisticas(self, obj):
        """Obtiene estadísticas del periodo (usando service)."""
        return PeriodoService.obtener_estadisticas_periodo(obj)

    def validate(self, data):
        """
        Valida que no exista otro periodo con el mismo nombre en la misma unidad.
        """
        unidad_academica = data.get('unidad_academica')
        nombre = data.get('nombre')

        queryset = Periodo.objects.filter(
            unidad_academica=unidad_academica,
            nombre=nombre
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                'nombre': f'Ya existe un periodo con este nombre en la unidad {unidad_academica.nombre}'
            })

        return data


class PeriodoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar periodos.
    """
    class Meta:
        model = Periodo
        fields = ['id', 'nombre', 'finalizado']


class BloqueHorarioSerializer(serializers.ModelSerializer):
    """
    Serializer para BloqueHorario.
    """
    dia_display = serializers.CharField(
        source='get_dia_display',
        read_only=True
    )
    duracion_horas = serializers.SerializerMethodField()

    class Meta:
        model = BloqueHorario
        fields = [
            'id',
            'carga',
            'dia',
            'dia_display',
            'hora_inicio',
            'hora_fin',
            'duracion_horas',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_duracion_horas(self, obj):
        """Calcula la duración del bloque usando el service."""
        return ValidadorHoras.calcular_duracion_bloque(obj)

    def validate(self, data):
        """
        Valida que hora_fin sea mayor que hora_inicio.
        """
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser mayor que la hora de inicio.'
            })

        return data


class BloqueHorarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear bloques horarios (sin el campo carga).
    Se usa dentro de CargaCreateUpdateSerializer.
    """
    dia_display = serializers.CharField(
        source='get_dia_display',
        read_only=True
    )

    class Meta:
        model = BloqueHorario
        fields = [
            'id',
            'dia',
            'dia_display',
            'hora_inicio',
            'hora_fin'
        ]

    def validate(self, data):
        """
        Valida que hora_fin sea mayor que hora_inicio.
        """
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise serializers.ValidationError({
                'hora_fin': 'La hora de fin debe ser mayor que la hora de inicio.'
            })

        return data


class CargaDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para Carga con información completa anidada.
    Usado para list y retrieve - devuelve objetos completos relacionados.
    """
    # Serializar objetos completos anidados
    programa_academico = ProgramaAcademicoSerializer(read_only=True)
    materia = MateriaSerializer(read_only=True)
    profesor = ProfesorSerializer(read_only=True)
    periodo = PeriodoSerializer(read_only=True)
    bloques = BloqueHorarioSerializer(many=True, read_only=True)

    # Campos adicionales
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    total_horas_bloques = serializers.SerializerMethodField()

    class Meta:
        model = Carga
        fields = [
            'id',
            'programa_academico',
            'materia',
            'profesor',
            'periodo',
            'bloques',
            'estado',
            'estado_display',
            'total_horas_bloques',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_horas_bloques(self, obj):
        """Calcula el total de horas usando el service."""
        return ValidadorHoras.calcular_total_horas_bloques(obj)


class CargaSerializer(serializers.ModelSerializer):
    """
    Serializer básico para Carga (lectura).
    Incluye solo campos simples con nombres expandidos.
    """
    programa_academico_nombre = serializers.CharField(
        source='programa_academico.nombre',
        read_only=True
    )
    materia_clave = serializers.CharField(
        source='materia.clave',
        read_only=True
    )
    materia_nombre = serializers.CharField(
        source='materia.nombre',
        read_only=True
    )
    materia_horas = serializers.IntegerField(
        source='materia.horas',
        read_only=True
    )
    profesor_nombre = serializers.CharField(
        source='profesor.nombre',
        read_only=True
    )
    periodo_nombre = serializers.CharField(
        source='periodo.nombre',
        read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display',
        read_only=True
    )
    bloques = BloqueHorarioSerializer(many=True, read_only=True)
    total_horas_bloques = serializers.SerializerMethodField()

    class Meta:
        model = Carga
        fields = [
            'id',
            'programa_academico',
            'programa_academico_nombre',
            'materia',
            'materia_clave',
            'materia_nombre',
            'materia_horas',
            'profesor',
            'profesor_nombre',
            'periodo',
            'periodo_nombre',
            'estado',
            'estado_display',
            'bloques',
            'total_horas_bloques',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_horas_bloques(self, obj):
        """Calcula el total de horas usando el service."""
        return ValidadorHoras.calcular_total_horas_bloques(obj)


class CargaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar cargas.
    """
    materia_clave = serializers.CharField(source='materia.clave', read_only=True)
    profesor_nombre = serializers.CharField(source='profesor.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Carga
        fields = [
            'id',
            'materia_clave',
            'profesor_nombre',
            'estado',
            'estado_display'
        ]


class CargaCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear/actualizar Carga.
    Permite guardado parcial (borrador):
    - profesor y bloques son opcionales para permitir estado PENDIENTE
    - Estado CORRECTA cuando tiene profesor y bloques completos
    """
    bloques = BloqueHorarioCreateSerializer(many=True, required=False)

    class Meta:
        model = Carga
        fields = [
            'id',
            'programa_academico',
            'materia',
            'profesor',
            'periodo',
            'estado',
            'bloques'
        ]
        read_only_fields = ['estado']  # El estado se calcula automáticamente
        extra_kwargs = {
            'profesor': {'required': False, 'allow_null': True},
        }

    def validate(self, data):
        """
        Valida:
        1. Que el periodo no esté finalizado
        2. Permite guardado parcial (sin profesor o sin bloques)
        """
        periodo = data.get('periodo', self.instance.periodo if self.instance else None)

        # Validar que el periodo no esté finalizado
        if periodo and periodo.finalizado:
            raise serializers.ValidationError({
                'periodo': 'No se pueden crear o modificar cargas en un periodo finalizado.'
            })

        return data

    def create(self, validated_data):
        """
        Crea una carga con sus bloques horarios.
        Permite crear sin bloques (guardado parcial).
        """
        bloques_data = validated_data.pop('bloques', [])

        # Crear la carga con estado PENDIENTE por defecto
        carga = Carga.objects.create(**validated_data)

        # Crear los bloques horarios si se proporcionaron
        if bloques_data:
            for bloque_data in bloques_data:
                BloqueHorario.objects.create(carga=carga, **bloque_data)

        # Calcular y actualizar el estado
        self._actualizar_estado(carga)

        return carga

    def update(self, instance, validated_data):
        """
        Actualiza una carga y sus bloques horarios.
        """
        bloques_data = validated_data.pop('bloques', None)

        # Actualizar campos de la carga
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Si se proporcionaron bloques, reemplazarlos
        if bloques_data is not None:
            # Eliminar bloques antiguos
            instance.bloques.all().delete()

            # Crear nuevos bloques
            for bloque_data in bloques_data:
                BloqueHorario.objects.create(carga=instance, **bloque_data)

        # Validar y actualizar el estado
        self._actualizar_estado(instance)

        return instance

    def _actualizar_estado(self, carga):
        """
        Actualiza el estado de la carga según su completitud:
        - PENDIENTE: Falta profesor o bloques horarios
        - CORRECTA: Tiene profesor y bloques horarios
        """
        tiene_profesor = carga.profesor is not None
        tiene_bloques = carga.bloques.exists()

        if tiene_profesor and tiene_bloques:
            carga.estado = Carga.Estado.CORRECTA
        else:
            carga.estado = Carga.Estado.PENDIENTE

        carga.save(update_fields=['estado'])
