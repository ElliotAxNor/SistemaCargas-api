from django.db import models
from apps.core.models import UnidadAcademica, ProgramaAcademico
from apps.academico.models import Profesor, Materia


class Periodo(models.Model):
    """
    Periodo académico (semestre).
    Puede ser finalizado por el responsable de unidad.
    """
    unidad_academica = models.ForeignKey(
        UnidadAcademica,
        on_delete=models.CASCADE,
        related_name='periodos'
    )
    nombre = models.CharField(
        max_length=50,
        help_text='Ejemplo: 2025-1, 2025-2'
    )
    finalizado = models.BooleanField(
        default=False,
        help_text='Indica si el periodo está cerrado'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'periodos'
        verbose_name = 'Periodo'
        verbose_name_plural = 'Periodos'
        ordering = ['-nombre']
        unique_together = [['unidad_academica', 'nombre']]

    def __str__(self):
        estado = 'Finalizado' if self.finalizado else 'Activo'
        return f"{self.nombre} - {self.unidad_academica.nombre} ({estado})"


class Carga(models.Model):
    """
    Asignación que vincula Materia + Profesor + Horario.
    Pertenece a un programa académico y un periodo.

    Estados:
    - PENDIENTE: Sin validar
    - ERRONEA: Conflicto de horario u horas incorrectas
    - CORRECTA: Validada sin conflictos
    """

    class Estado(models.TextChoices):
        ERRONEA = 'ERRONEA', 'Errónea'
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CORRECTA = 'CORRECTA', 'Correcta'

    programa_academico = models.ForeignKey(
        ProgramaAcademico,
        on_delete=models.CASCADE,
        related_name='cargas'
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='cargas'
    )
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='cargas'
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='cargas'
    )
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cargas'
        verbose_name = 'Carga'
        verbose_name_plural = 'Cargas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profesor', 'periodo']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return (
            f"{self.materia.clave} - {self.profesor.nombre} "
            f"({self.periodo.nombre}) [{self.get_estado_display()}]"
        )


class BloqueHorario(models.Model):
    """
    Define día y rango de horas para una carga.
    Una carga puede tener múltiples bloques
    (ej: Lunes 8-10 y Miércoles 8-10).
    """

    class Dia(models.TextChoices):
        LUNES = 'LUN', 'Lunes'
        MARTES = 'MAR', 'Martes'
        MIERCOLES = 'MIE', 'Miércoles'
        JUEVES = 'JUE', 'Jueves'
        VIERNES = 'VIE', 'Viernes'
        SABADO = 'SAB', 'Sábado'
        DOMINGO = 'DOM', 'Domingo'

    carga = models.ForeignKey(
        Carga,
        on_delete=models.CASCADE,
        related_name='bloques'
    )
    dia = models.CharField(
        max_length=3,
        choices=Dia.choices
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bloques_horarios'
        verbose_name = 'Bloque Horario'
        verbose_name_plural = 'Bloques Horarios'
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        return (
            f"{self.get_dia_display()} "
            f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')}"
        )
