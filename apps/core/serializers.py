"""
Serializers para el módulo Core.
"""

from rest_framework import serializers
from .models import UnidadAcademica, ProgramaAcademico, Usuario


class UnidadAcademicaSerializer(serializers.ModelSerializer):
    """
    Serializer para UnidadAcademica.
    """
    total_programas = serializers.SerializerMethodField()

    class Meta:
        model = UnidadAcademica
        fields = [
            'id',
            'nombre',
            'total_programas',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_programas(self, obj):
        """Retorna el total de programas académicos de la unidad."""
        return obj.programas.count()


class ProgramaAcademicoSerializer(serializers.ModelSerializer):
    """
    Serializer para ProgramaAcademico.
    """
    unidad_academica_nombre = serializers.CharField(
        source='unidad_academica.nombre',
        read_only=True
    )
    total_materias = serializers.SerializerMethodField()

    class Meta:
        model = ProgramaAcademico
        fields = [
            'id',
            'unidad_academica',
            'unidad_academica_nombre',
            'nombre',
            'total_materias',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_total_materias(self, obj):
        """Retorna el total de materias del programa."""
        return obj.materias.count()


class ProgramaAcademicoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar programas (sin campos anidados).
    """
    class Meta:
        model = ProgramaAcademico
        fields = ['id', 'nombre']


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para Usuario (lectura).
    Incluye información completa de unidad/programa según el rol.
    """
    unidad_academica_nombre = serializers.CharField(
        source='unidad_academica.nombre',
        read_only=True
    )
    programa_academico_nombre = serializers.CharField(
        source='programa_academico.nombre',
        read_only=True
    )
    rol_display = serializers.CharField(
        source='get_rol_display',
        read_only=True
    )
    # Campo calculado: unidad académica efectiva (directa o a través del programa)
    unidad_academica_efectiva = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'rol',
            'rol_display',
            'unidad_academica',
            'unidad_academica_nombre',
            'unidad_academica_efectiva',
            'programa_academico',
            'programa_academico_nombre',
            'is_active',
            'date_joined'
        ]
        read_only_fields = ['date_joined']

    def get_unidad_academica_efectiva(self, obj):
        """
        Retorna el ID de la unidad académica del usuario.
        - Si es RESP_UNIDAD: retorna su unidad_academica directa
        - Si es RESP_PROGRAMA: retorna la unidad_academica de su programa
        """
        if obj.unidad_academica_id:
            return obj.unidad_academica_id
        elif obj.programa_academico_id and obj.programa_academico:
            return obj.programa_academico.unidad_academica_id
        return None


class UsuarioCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear/actualizar Usuario.
    Incluye validación de contraseña y coherencia rol-relación.
    """
    password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'rol',
            'unidad_academica',
            'programa_academico',
            'is_active'
        ]

    def validate(self, data):
        """
        Valida que el usuario tenga la relación correcta según su rol.
        """
        rol = data.get('rol', self.instance.rol if self.instance else None)
        unidad = data.get('unidad_academica', self.instance.unidad_academica if self.instance else None)
        programa = data.get('programa_academico', self.instance.programa_academico if self.instance else None)

        if rol == Usuario.Rol.RESP_UNIDAD:
            if not unidad:
                raise serializers.ValidationError({
                    'unidad_academica': 'Un responsable de unidad debe estar asociado a una unidad académica.'
                })
            if programa:
                raise serializers.ValidationError({
                    'programa_academico': 'Un responsable de unidad no puede estar asociado a un programa.'
                })

        elif rol == Usuario.Rol.RESP_PROGRAMA:
            if not programa:
                raise serializers.ValidationError({
                    'programa_academico': 'Un responsable de programa debe estar asociado a un programa académico.'
                })
            if unidad:
                raise serializers.ValidationError({
                    'unidad_academica': 'Un responsable de programa no puede estar asociado a una unidad.'
                })

        return data

    def create(self, validated_data):
        """
        Crea un usuario y hashea la contraseña.
        """
        password = validated_data.pop('password', None)
        usuario = Usuario(**validated_data)

        if password:
            usuario.set_password(password)
        else:
            # Genera una contraseña aleatoria si no se proporciona
            usuario.set_unusable_password()

        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        """
        Actualiza un usuario y hashea la contraseña si se proporciona.
        """
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class UsuarioListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar usuarios.
    """
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    programa_academico_nombre = serializers.CharField(
        source='programa_academico.nombre',
        read_only=True
    )
    unidad_academica_nombre = serializers.CharField(
        source='unidad_academica.nombre',
        read_only=True
    )

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'rol',
            'rol_display',
            'programa_academico',
            'programa_academico_nombre',
            'unidad_academica',
            'unidad_academica_nombre'
        ]
