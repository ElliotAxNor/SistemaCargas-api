"""
Servicio para validación de conflictos de horarios entre cargas.
"""

from typing import List, Optional, Dict
from apps.asignaciones.models import Carga, BloqueHorario, Periodo
from apps.academico.models import Profesor


class ValidadorConflictos:
    """
    Servicio para detectar conflictos de horarios entre cargas.
    Previene que un profesor sea asignado a dos materias con horarios que se solapan.
    """

    @staticmethod
    def bloques_se_solapan(bloque1: BloqueHorario, bloque2: BloqueHorario) -> bool:
        """
        Verifica si dos bloques horarios se solapan.
        Solo hay solapamiento si es el mismo día y los horarios se cruzan.

        Args:
            bloque1: Primera instancia de BloqueHorario
            bloque2: Segunda instancia de BloqueHorario

        Returns:
            bool: True si hay solapamiento, False en caso contrario
        """
        if bloque1.dia != bloque2.dia:
            return False

        # Verificar solapamiento de horarios
        # No hay solapamiento si un bloque termina antes de que empiece el otro
        return not (
            bloque1.hora_fin <= bloque2.hora_inicio or
            bloque1.hora_inicio >= bloque2.hora_fin
        )

    @staticmethod
    def obtener_cargas_profesor_periodo(profesor: Profesor, periodo: Periodo) -> List[Carga]:
        """
        Obtiene todas las cargas de un profesor en un periodo específico.

        Args:
            profesor: Instancia de Profesor
            periodo: Instancia de Periodo

        Returns:
            List[Carga]: Lista de cargas del profesor en el periodo
        """
        return Carga.objects.filter(
            profesor=profesor,
            periodo=periodo
        ).prefetch_related('bloques')

    @staticmethod
    def detectar_conflicto_carga(carga: Carga) -> Optional[Dict]:
        """
        Detecta si una carga tiene conflictos de horario con otras cargas
        del mismo profesor en el mismo periodo.

        Args:
            carga: Instancia de Carga a validar

        Returns:
            Dict con información del conflicto si existe, None si no hay conflicto.
            Formato del dict:
            {
                'tiene_conflicto': bool,
                'carga_conflictiva': Carga,
                'programa': str,
                'materia': str,
                'bloques_conflictivos': [(BloqueHorario, BloqueHorario)]
            }
        """
        # Obtener todas las cargas del profesor en el mismo periodo (excluyendo la actual)
        otras_cargas = ValidadorConflictos.obtener_cargas_profesor_periodo(
            carga.profesor,
            carga.periodo
        ).exclude(id=carga.id)

        bloques_carga = carga.bloques.all()

        # Verificar cada carga existente
        for otra_carga in otras_cargas:
            bloques_otra_carga = otra_carga.bloques.all()

            # Verificar si algún bloque se solapa
            bloques_conflictivos = []
            for bloque in bloques_carga:
                for otro_bloque in bloques_otra_carga:
                    if ValidadorConflictos.bloques_se_solapan(bloque, otro_bloque):
                        bloques_conflictivos.append((bloque, otro_bloque))

            # Si hay bloques que se solapan, retornar el conflicto
            if bloques_conflictivos:
                return {
                    'tiene_conflicto': True,
                    'carga_conflictiva': otra_carga,
                    'programa': otra_carga.programa_academico.nombre,
                    'materia': otra_carga.materia.nombre,
                    'materia_clave': otra_carga.materia.clave,
                    'bloques_conflictivos': bloques_conflictivos
                }

        return None

    @staticmethod
    def validar_disponibilidad_profesor(
        profesor: Profesor,
        periodo: Periodo,
        bloques: List[BloqueHorario],
        excluir_carga_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Valida si un profesor está disponible para nuevos bloques horarios.
        Útil para validar ANTES de crear una carga.

        Args:
            profesor: Instancia de Profesor
            periodo: Instancia de Periodo
            bloques: Lista de BloqueHorario a validar
            excluir_carga_id: ID de carga a excluir (útil al editar una carga existente)

        Returns:
            Dict con información del conflicto si existe, None si el profesor está disponible
        """
        cargas_existentes = ValidadorConflictos.obtener_cargas_profesor_periodo(
            profesor,
            periodo
        )

        if excluir_carga_id:
            cargas_existentes = cargas_existentes.exclude(id=excluir_carga_id)

        # Verificar cada carga existente
        for carga in cargas_existentes:
            bloques_carga = carga.bloques.all()

            bloques_conflictivos = []
            for bloque_nuevo in bloques:
                for bloque_existente in bloques_carga:
                    if ValidadorConflictos.bloques_se_solapan(bloque_nuevo, bloque_existente):
                        bloques_conflictivos.append((bloque_nuevo, bloque_existente))

            if bloques_conflictivos:
                return {
                    'tiene_conflicto': True,
                    'carga_conflictiva': carga,
                    'programa': carga.programa_academico.nombre,
                    'materia': carga.materia.nombre,
                    'materia_clave': carga.materia.clave,
                    'bloques_conflictivos': bloques_conflictivos
                }

        return None
