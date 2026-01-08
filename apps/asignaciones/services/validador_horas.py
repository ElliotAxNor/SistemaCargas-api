"""
Servicio para validación de horas entre bloques horarios y materias.
"""

from datetime import datetime
from typing import List
from apps.asignaciones.models import Carga, BloqueHorario


class ValidadorHoras:
    """
    Servicio para validar que las horas de los bloques horarios
    coincidan con las horas definidas en la materia.
    """

    @staticmethod
    def calcular_duracion_bloque(bloque: BloqueHorario) -> float:
        """
        Calcula la duración de un bloque horario en horas.

        Args:
            bloque: Instancia de BloqueHorario

        Returns:
            float: Duración en horas
        """
        inicio = datetime.combine(datetime.today(), bloque.hora_inicio)
        fin = datetime.combine(datetime.today(), bloque.hora_fin)
        duracion = fin - inicio
        return duracion.total_seconds() / 3600

    @staticmethod
    def calcular_total_horas_bloques(carga: Carga) -> float:
        """
        Calcula el total de horas asignadas en los bloques horarios de una carga.

        Args:
            carga: Instancia de Carga

        Returns:
            float: Total de horas
        """
        total = 0
        for bloque in carga.bloques.all():
            total += ValidadorHoras.calcular_duracion_bloque(bloque)
        return total

    @staticmethod
    def validar_horas_carga(carga: Carga) -> bool:
        """
        Verifica que la suma de horas de los bloques coincida
        con las horas definidas en la materia.

        Args:
            carga: Instancia de Carga

        Returns:
            bool: True si las horas coinciden, False en caso contrario
        """
        total_bloques = ValidadorHoras.calcular_total_horas_bloques(carga)
        return total_bloques == carga.materia.horas

    @staticmethod
    def validar_horas_bloques(bloques: List[BloqueHorario], horas_materia: int) -> bool:
        """
        Verifica que la suma de horas de una lista de bloques coincida
        con las horas de la materia (útil para validar antes de crear la carga).

        Args:
            bloques: Lista de instancias de BloqueHorario
            horas_materia: Horas definidas en la materia

        Returns:
            bool: True si las horas coinciden, False en caso contrario
        """
        total = sum(ValidadorHoras.calcular_duracion_bloque(b) for b in bloques)
        return total == horas_materia
