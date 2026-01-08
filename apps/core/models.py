from django.contrib.auth.models import AbstractUser
from django.db import models


class UnidadAcademica(models.Model):
    """
    Contenedor principal que agrupa programas académicos y profesores.
    """
    nombre = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unidades_academicas'
        verbose_name = 'Unidad Académica'
        verbose_name_plural = 'Unidades Académicas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ProgramaAcademico(models.Model):
    """
    Programa académico que pertenece a una Unidad Académica.
    """
    unidad_academica = models.ForeignKey(
        UnidadAcademica,
        on_delete=models.CASCADE,
        related_name='programas'
    )
    nombre = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'programas_academicos'
        verbose_name = 'Programa Académico'
        verbose_name_plural = 'Programas Académicos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.unidad_academica.nombre})"


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado.

    Roles:
    - RESP_UNIDAD: Responsable de Unidad Académica (gestiona accesos, visualiza todo)
    - RESP_PROGRAMA: Responsable de Programa (gestiona materias, crea cargas)

    Relaciones:
    - Una Unidad Académica tiene exactamente un responsable de unidad (1:1)
    - Un Programa Académico tiene exactamente un responsable de programa (1:1)
    """

    class Rol(models.TextChoices):
        RESP_UNIDAD = 'RESP_UNIDAD', 'Responsable de Unidad'
        RESP_PROGRAMA = 'RESP_PROGRAMA', 'Responsable de Programa'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        null=True,
        blank=True,
    )
    unidad_academica = models.OneToOneField(
        UnidadAcademica,
        on_delete=models.CASCADE,
        related_name='responsable',
        null=True,
        blank=True,
        help_text='Unidad Académica si el rol es RESP_UNIDAD'
    )
    programa_academico = models.OneToOneField(
        ProgramaAcademico,
        on_delete=models.CASCADE,
        related_name='responsable',
        null=True,
        blank=True,
        help_text='Programa Académico si el rol es RESP_PROGRAMA'
    )

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    def clean(self):
        """
        Valida que el usuario tenga la relación correcta según su rol.
        """
        from django.core.exceptions import ValidationError

        if self.rol == self.Rol.RESP_UNIDAD:
            if not self.unidad_academica:
                raise ValidationError('Un responsable de unidad debe estar asociado a una unidad académica.')
            if self.programa_academico:
                raise ValidationError('Un responsable de unidad no puede estar asociado a un programa.')

        elif self.rol == self.Rol.RESP_PROGRAMA:
            if not self.programa_academico:
                raise ValidationError('Un responsable de programa debe estar asociado a un programa académico.')
            if self.unidad_academica:
                raise ValidationError('Un responsable de programa no puede estar asociado a una unidad.')
