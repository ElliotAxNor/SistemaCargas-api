"""
Servicio para la gestión de periodos académicos.
"""

from typing import Dict, List
from apps.asignaciones.models import Periodo, Carga


class PeriodoService:
    """
    Servicio para gestionar la lógica de negocio relacionada con periodos académicos.
    """

    @staticmethod
    def puede_finalizar(periodo: Periodo) -> bool:
        """
        Verifica si un periodo puede ser finalizado.
        Solo puede finalizar si no hay cargas erróneas o pendientes.

        Args:
            periodo: Instancia de Periodo

        Returns:
            bool: True si puede finalizar, False en caso contrario
        """
        cargas_problematicas = periodo.cargas.exclude(
            estado=Carga.Estado.CORRECTA
        )
        return not cargas_problematicas.exists()

    @staticmethod
    def obtener_cargas_problematicas(periodo: Periodo) -> Dict[str, List[Carga]]:
        """
        Obtiene las cargas que impiden finalizar un periodo,
        agrupadas por estado.

        Args:
            periodo: Instancia de Periodo

        Returns:
            Dict con listas de cargas erróneas y pendientes
        """
        return {
            'erroneas': list(periodo.cargas.filter(estado=Carga.Estado.ERRONEA)),
            'pendientes': list(periodo.cargas.filter(estado=Carga.Estado.PENDIENTE))
        }

    @staticmethod
    def finalizar_periodo(periodo: Periodo) -> Dict:
        """
        Intenta finalizar un periodo.
        Valida que no haya cargas problemáticas antes de finalizar.

        Args:
            periodo: Instancia de Periodo

        Returns:
            Dict con el resultado de la operación:
            {
                'success': bool,
                'mensaje': str,
                'cargas_problematicas': Dict (solo si success=False)
            }
        """
        if periodo.finalizado:
            return {
                'success': False,
                'mensaje': 'El periodo ya está finalizado'
            }

        if not PeriodoService.puede_finalizar(periodo):
            cargas_problematicas = PeriodoService.obtener_cargas_problematicas(periodo)
            total_problemas = (
                len(cargas_problematicas['erroneas']) +
                len(cargas_problematicas['pendientes'])
            )

            return {
                'success': False,
                'mensaje': f'No se puede finalizar el periodo. Hay {total_problemas} carga(s) con problemas.',
                'cargas_problematicas': cargas_problematicas
            }

        # Finalizar el periodo
        periodo.finalizado = True
        periodo.save(update_fields=['finalizado'])

        return {
            'success': True,
            'mensaje': 'Periodo finalizado exitosamente'
        }

    @staticmethod
    def obtener_estadisticas_periodo(periodo: Periodo) -> Dict:
        """
        Obtiene estadísticas del periodo (útil para dashboard).

        Args:
            periodo: Instancia de Periodo

        Returns:
            Dict con estadísticas del periodo
        """
        total_cargas = periodo.cargas.count()
        cargas_por_estado = {
            'correctas': periodo.cargas.filter(estado=Carga.Estado.CORRECTA).count(),
            'pendientes': periodo.cargas.filter(estado=Carga.Estado.PENDIENTE).count(),
            'erroneas': periodo.cargas.filter(estado=Carga.Estado.ERRONEA).count(),
        }

        porcentaje_completado = 0
        if total_cargas > 0:
            porcentaje_completado = (cargas_por_estado['correctas'] / total_cargas) * 100

        return {
            'total_cargas': total_cargas,
            'cargas_por_estado': cargas_por_estado,
            'porcentaje_completado': round(porcentaje_completado, 2),
            'puede_finalizar': PeriodoService.puede_finalizar(periodo),
            'finalizado': periodo.finalizado
        }
