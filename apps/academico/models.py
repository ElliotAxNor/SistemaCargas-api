from django.db import models
from apps.core.models import UnidadAcademica, ProgramaAcademico


class Profesor(models.Model):
    """
    Recurso compartido a nivel de Unidad Académica.
    Un profesor puede ser asignado a materias de diferentes programas
    dentro de la misma unidad.
    """
    unidad_academica = models.ForeignKey(
        UnidadAcademica,
        on_delete=models.CASCADE,
        related_name='profesores'
    )
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profesores'
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
        ordering = ['nombre']
        unique_together = [['unidad_academica', 'email']]

    def __str__(self):
        return f"{self.nombre} - {self.unidad_academica.nombre}"


class Materia(models.Model):
    """
    Materia que pertenece a un Programa Académico.
    Una materia puede tener múltiples cargas (secciones) con diferentes
    profesores y horarios.
    """
    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        on_delete=models.CASCADE,
        related_name='materias'
    )
    clave = models.CharField(
        max_length=50,
        help_text='Clave única de la materia'
    )
    nombre = models.CharField(max_length=255)
    horas = models.PositiveIntegerField(
        help_text='Horas semanales de la materia'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['clave']
        unique_together = [['programa_academico', 'clave']]

    def __str__(self):
        return f"{self.clave} - {self.nombre}"
