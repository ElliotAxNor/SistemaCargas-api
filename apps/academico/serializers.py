"""
Serializers para el módulo Académico.
"""

from rest_framework import serializers
from .models import Profesor, Materia


class ProfesorSerializer(serializers.ModelSerializer):
    """
    Serializer para Profesor.
    """
    unidad_academica_nombre = serializers.CharField(
        source='unidad_academica.nombre',
        read_only=True
    )
    total_cargas = serializers.SerializerMethodField()

    class Meta:
        model = Profesor
        fields = [
            'id',
            'unidad_academica',
            'unidad_academica_nombre',
            'nombre',
            'email',
            'total_cargas',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_cargas(self, obj):
        """Retorna el total de cargas asignadas al profesor."""
        return obj.cargas.count()

    def validate(self, data):
        """
        Valida que no exista otro profesor con el mismo email en la misma unidad.
        """
        unidad_academica = data.get('unidad_academica')
        email = data.get('email')

        # Excluir la instancia actual si estamos actualizando
        queryset = Profesor.objects.filter(
            unidad_academica=unidad_academica,
            email=email
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                'email': f'Ya existe un profesor con este email en la unidad {unidad_academica.nombre}'
            })

        return data


class ProfesorListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar profesores.
    """
    class Meta:
        model = Profesor
        fields = ['id', 'nombre', 'email']


class MateriaSerializer(serializers.ModelSerializer):
    """
    Serializer para Materia.
    """
    programa_academico_nombre = serializers.CharField(
        source='programa_academico.nombre',
        read_only=True
    )
    total_cargas = serializers.SerializerMethodField()

    class Meta:
        model = Materia
        fields = [
            'id',
            'programa_academico',
            'programa_academico_nombre',
            'clave',
            'nombre',
            'horas',
            'total_cargas',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_cargas(self, obj):
        """Retorna el total de cargas (secciones) de la materia."""
        return obj.cargas.count()

    def validate_horas(self, value):
        """
        Valida que las horas sean positivas.
        """
        if value <= 0:
            raise serializers.ValidationError('Las horas deben ser mayores a 0.')
        return value

    def validate(self, data):
        """
        Valida que no exista otra materia con la misma clave en el mismo programa.
        """
        programa_academico = data.get('programa_academico')
        clave = data.get('clave')

        # Excluir la instancia actual si estamos actualizando
        queryset = Materia.objects.filter(
            programa_academico=programa_academico,
            clave=clave
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                'clave': f'Ya existe una materia con esta clave en el programa {programa_academico.nombre}'
            })

        return data


class MateriaListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar materias.
    """
    class Meta:
        model = Materia
        fields = ['id', 'clave', 'nombre', 'horas']
