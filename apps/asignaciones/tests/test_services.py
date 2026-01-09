"""
Tests para los Services de Asignaciones.
"""

from django.test import TestCase
from datetime import time

from apps.core.models import UnidadAcademica, ProgramaAcademico
from apps.academico.models import Profesor, Materia
from apps.asignaciones.models import Periodo, Carga, BloqueHorario
from apps.asignaciones.services import (
    ValidadorConflictos,
    ValidadorHoras,
    PeriodoService
)


class ValidadorHorasTestCase(TestCase):
    """Tests para ValidadorHoras service."""

    def setUp(self):
        """Configuración inicial para cada test."""
        # Crear datos base
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Software"
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre="Dr. Juan Pérez",
            email="juan@test.com"
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave="CS101",
            nombre="Programación I",
            horas=6
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre="2025-1"
        )

    def test_calcular_duracion_bloque(self):
        """Test: Calcular duración de un bloque horario."""
        bloque = BloqueHorario(
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        duracion = ValidadorHoras.calcular_duracion_bloque(bloque)
        self.assertEqual(duracion, 2.0)

    def test_validar_horas_carga_correcta(self):
        """Test: Validar carga con horas correctas."""
        # Crear carga
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

        # Crear bloques que sumen 6 horas
        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)  # 2 horas
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='MIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)  # 2 horas
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='VIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)  # 2 horas
        )

        # Validar
        total_horas = ValidadorHoras.calcular_total_horas_bloques(carga)
        self.assertEqual(total_horas, 6.0)

        es_valida = ValidadorHoras.validar_horas_carga(carga)
        self.assertTrue(es_valida)

    def test_validar_horas_carga_incorrecta(self):
        """Test: Validar carga con horas incorrectas."""
        # Crear carga
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,  # materia tiene 6 horas
            profesor=self.profesor,
            periodo=self.periodo
        )

        # Crear bloque que suma solo 2 horas
        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)  # 2 horas
        )

        # Validar
        total_horas = ValidadorHoras.calcular_total_horas_bloques(carga)
        self.assertEqual(total_horas, 2.0)

        es_valida = ValidadorHoras.validar_horas_carga(carga)
        self.assertFalse(es_valida)

    def test_validar_horas_bloques_lista(self):
        """Test: Validar lista de bloques antes de crear la carga."""
        bloques = [
            BloqueHorario(dia='LUN', hora_inicio=time(8, 0), hora_fin=time(10, 0)),
            BloqueHorario(dia='MIE', hora_inicio=time(8, 0), hora_fin=time(11, 0)),
            BloqueHorario(dia='VIE', hora_inicio=time(8, 0), hora_fin=time(11, 0))
        ]

        # Total: 2 + 3 + 3 = 8 horas
        es_valida = ValidadorHoras.validar_horas_bloques(bloques, 8)
        self.assertTrue(es_valida)

        # Comparar con 6 horas
        es_valida = ValidadorHoras.validar_horas_bloques(bloques, 6)
        self.assertFalse(es_valida)


class ValidadorConflictosTestCase(TestCase):
    """Tests para ValidadorConflictos service."""

    def setUp(self):
        """Configuración inicial para cada test."""
        # Crear datos base
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa1 = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Software"
        )
        self.programa2 = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Computación"
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre="Dr. Juan Pérez",
            email="juan@test.com"
        )
        self.materia1 = Materia.objects.create(
            programa_academico=self.programa1,
            clave="CS101",
            nombre="Programación I",
            horas=6
        )
        self.materia2 = Materia.objects.create(
            programa_academico=self.programa2,
            clave="CC101",
            nombre="Algoritmos",
            horas=6
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre="2025-1"
        )

    def test_bloques_se_solapan_mismo_dia(self):
        """Test: Detectar solapamiento en el mismo día."""
        bloque1 = BloqueHorario(
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        bloque2 = BloqueHorario(
            dia='LUN',
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0)
        )

        se_solapan = ValidadorConflictos.bloques_se_solapan(bloque1, bloque2)
        self.assertTrue(se_solapan)

    def test_bloques_no_se_solapan_mismo_dia(self):
        """Test: No hay solapamiento si los horarios no se cruzan."""
        bloque1 = BloqueHorario(
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        bloque2 = BloqueHorario(
            dia='LUN',
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0)
        )

        se_solapan = ValidadorConflictos.bloques_se_solapan(bloque1, bloque2)
        self.assertFalse(se_solapan)

    def test_bloques_no_se_solapan_diferente_dia(self):
        """Test: No hay solapamiento si es diferente día."""
        bloque1 = BloqueHorario(
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        bloque2 = BloqueHorario(
            dia='MAR',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        se_solapan = ValidadorConflictos.bloques_se_solapan(bloque1, bloque2)
        self.assertFalse(se_solapan)

    def test_detectar_conflicto_carga(self):
        """Test: Detectar conflicto en una carga existente."""
        # Crear primera carga
        carga1 = Carga.objects.create(
            programa_academico=self.programa1,
            materia=self.materia1,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga1,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Crear segunda carga con el mismo profesor en horario solapado
        carga2 = Carga.objects.create(
            programa_academico=self.programa2,
            materia=self.materia2,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga2,
            dia='LUN',
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0)
        )

        # Detectar conflicto
        conflicto = ValidadorConflictos.detectar_conflicto_carga(carga2)

        self.assertIsNotNone(conflicto)
        self.assertTrue(conflicto['tiene_conflicto'])
        self.assertEqual(conflicto['carga_conflictiva'].id, carga1.id)

    def test_no_detectar_conflicto_sin_solapamiento(self):
        """Test: No detectar conflicto si no hay solapamiento."""
        # Crear primera carga
        carga1 = Carga.objects.create(
            programa_academico=self.programa1,
            materia=self.materia1,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga1,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Crear segunda carga con el mismo profesor pero sin solapamiento
        carga2 = Carga.objects.create(
            programa_academico=self.programa2,
            materia=self.materia2,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga2,
            dia='MIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Detectar conflicto
        conflicto = ValidadorConflictos.detectar_conflicto_carga(carga2)

        self.assertIsNone(conflicto)

    def test_validar_disponibilidad_profesor_ocupado(self):
        """Test: Validar disponibilidad de profesor ocupado."""
        # Crear carga existente
        carga = Carga.objects.create(
            programa_academico=self.programa1,
            materia=self.materia1,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Intentar validar nuevos bloques en el mismo horario
        nuevos_bloques = [
            BloqueHorario(dia='LUN', hora_inicio=time(9, 0), hora_fin=time(11, 0))
        ]

        conflicto = ValidadorConflictos.validar_disponibilidad_profesor(
            profesor=self.profesor,
            periodo=self.periodo,
            bloques=nuevos_bloques
        )

        self.assertIsNotNone(conflicto)
        self.assertTrue(conflicto['tiene_conflicto'])

    def test_validar_disponibilidad_profesor_disponible(self):
        """Test: Validar disponibilidad de profesor disponible."""
        # Crear carga existente
        carga = Carga.objects.create(
            programa_academico=self.programa1,
            materia=self.materia1,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Intentar validar nuevos bloques en diferente horario
        nuevos_bloques = [
            BloqueHorario(dia='MIE', hora_inicio=time(8, 0), hora_fin=time(10, 0))
        ]

        conflicto = ValidadorConflictos.validar_disponibilidad_profesor(
            profesor=self.profesor,
            periodo=self.periodo,
            bloques=nuevos_bloques
        )

        self.assertIsNone(conflicto)


class PeriodoServiceTestCase(TestCase):
    """Tests para PeriodoService."""

    def setUp(self):
        """Configuración inicial para cada test."""
        # Crear datos base
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Software"
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre="Dr. Juan Pérez",
            email="juan@test.com"
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave="CS101",
            nombre="Programación I",
            horas=6
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre="2025-1"
        )

    def test_puede_finalizar_sin_cargas(self):
        """Test: Periodo sin cargas puede finalizar."""
        puede = PeriodoService.puede_finalizar(self.periodo)
        self.assertTrue(puede)

    def test_puede_finalizar_solo_cargas_correctas(self):
        """Test: Periodo con solo cargas correctas puede finalizar."""
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.CORRECTA
        )

        puede = PeriodoService.puede_finalizar(self.periodo)
        self.assertTrue(puede)

    def test_no_puede_finalizar_con_cargas_pendientes(self):
        """Test: Periodo con cargas pendientes no puede finalizar."""
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.PENDIENTE
        )

        puede = PeriodoService.puede_finalizar(self.periodo)
        self.assertFalse(puede)

    def test_no_puede_finalizar_con_cargas_pendientes_por_falta_de_profesor(self):
        """Test: Periodo con cargas pendientes (sin profesor) no puede finalizar."""
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=None,
            periodo=self.periodo,
            estado=Carga.Estado.PENDIENTE
        )

        puede = PeriodoService.puede_finalizar(self.periodo)
        self.assertFalse(puede)

    def test_finalizar_periodo_exitoso(self):
        """Test: Finalizar periodo exitosamente."""
        # Crear solo cargas correctas
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.CORRECTA
        )

        resultado = PeriodoService.finalizar_periodo(self.periodo)

        self.assertTrue(resultado['success'])
        self.periodo.refresh_from_db()
        self.assertTrue(self.periodo.finalizado)

    def test_finalizar_periodo_con_problemas(self):
        """Test: No finalizar periodo con cargas problemáticas."""
        # Crear carga pendiente
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.PENDIENTE
        )

        resultado = PeriodoService.finalizar_periodo(self.periodo)

        self.assertFalse(resultado['success'])
        self.assertIn('cargas_problematicas', resultado)
        self.periodo.refresh_from_db()
        self.assertFalse(self.periodo.finalizado)

    def test_obtener_estadisticas_periodo(self):
        """Test: Obtener estadísticas de un periodo."""
        # Crear cargas de diferentes estados
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.CORRECTA
        )
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.CORRECTA
        )
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.PENDIENTE
        )

        stats = PeriodoService.obtener_estadisticas_periodo(self.periodo)

        self.assertEqual(stats['total_cargas'], 3)
        self.assertEqual(stats['cargas_por_estado']['correctas'], 2)
        self.assertEqual(stats['cargas_por_estado']['pendientes'], 1)
        self.assertAlmostEqual(stats['porcentaje_completado'], 66.67, places=1)
        self.assertFalse(stats['puede_finalizar'])
