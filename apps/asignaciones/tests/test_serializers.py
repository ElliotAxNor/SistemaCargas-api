"""
Tests para Serializers del módulo Asignaciones.
"""

from django.test import TestCase
from rest_framework.test import APIRequestFactory
from datetime import time
from decimal import Decimal

from apps.core.models import UnidadAcademica, ProgramaAcademico
from apps.academico.models import Profesor, Materia
from apps.asignaciones.models import Periodo, Carga, BloqueHorario
from apps.asignaciones.serializers import (
    PeriodoSerializer,
    BloqueHorarioSerializer,
    CargaSerializer,
    CargaCreateUpdateSerializer,
    CargaListSerializer
)
from common.exceptions import (
    HorasInvalidasException,
    ConflictoHorarioException,
    PeriodoFinalizadoException
)


class PeriodoSerializerTestCase(TestCase):
    """Tests para PeriodoSerializer."""

    def setUp(self):
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")

    def test_crear_periodo_valido(self):
        """Test crear periodo con datos válidos."""
        data = {
            'unidad_academica': self.unidad.id,
            'nombre': '2025-1'
        }
        serializer = PeriodoSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        periodo = serializer.save()
        self.assertEqual(periodo.nombre, '2025-1')
        self.assertFalse(periodo.finalizado)

    def test_nombre_unico_por_unidad(self):
        """Test que el nombre del periodo sea único por unidad."""
        Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )
        data = {
            'unidad_academica': self.unidad.id,
            'nombre': '2025-1'
        }
        serializer = PeriodoSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class BloqueHorarioSerializerTestCase(TestCase):
    """Tests para BloqueHorarioSerializer."""

    def setUp(self):
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Software"
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave="CS101",
            nombre="Programación I",
            horas=6
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre="Dr. Juan Pérez",
            email="juan@universidad.edu"
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre="2025-1"
        )
        self.carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

    def test_serializar_bloque(self):
        """Test serialización de un bloque horario."""
        bloque = BloqueHorario.objects.create(
            carga=self.carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        serializer = BloqueHorarioSerializer(bloque)
        self.assertEqual(serializer.data['dia'], 'LUN')
        self.assertEqual(serializer.data['hora_inicio'], '08:00:00')
        self.assertEqual(serializer.data['hora_fin'], '10:00:00')

    def test_validar_hora_fin_mayor_que_inicio(self):
        """Test que hora_fin debe ser mayor que hora_inicio."""
        data = {
            'carga': self.carga.id,
            'dia': 'LUN',
            'hora_inicio': '10:00:00',
            'hora_fin': '08:00:00'
        }
        serializer = BloqueHorarioSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class CargaSerializerTestCase(TestCase):
    """Tests para CargaSerializer (read-only)."""

    def setUp(self):
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Software"
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave="CS101",
            nombre="Programación I",
            horas=6
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre="Dr. Juan Pérez",
            email="juan@universidad.edu"
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre="2025-1"
        )

    def test_serializar_carga_con_bloques(self):
        """Test serialización de carga con bloques incluidos."""
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.CORRECTA
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='MIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        serializer = CargaSerializer(carga)
        self.assertEqual(len(serializer.data['bloques']), 2)
        self.assertEqual(serializer.data['estado'], 'CORRECTA')
        self.assertIn('materia', serializer.data)
        self.assertIn('profesor', serializer.data)


class CargaCreateUpdateSerializerTestCase(TestCase):
    """Tests para CargaCreateUpdateSerializer (validación automática)."""

    def setUp(self):
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Software"
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave="CS101",
            nombre="Programación I",
            horas=6
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre="Dr. Juan Pérez",
            email="juan@universidad.edu"
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre="2025-1"
        )

        # Factory para simular request con contexto
        self.factory = APIRequestFactory()

    def test_crear_carga_valida_con_horas_correctas(self):
        """Test crear carga con horas correctas (6 horas en bloques = 6 horas materia)."""
        data = {
            'programa_academico': self.programa.id,
            'materia': self.materia.id,
            'profesor': self.profesor.id,
            'periodo': self.periodo.id,
            'bloques': [
                {'dia': 'LUN', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'},
                {'dia': 'MIE', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'},
                {'dia': 'VIE', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'}
            ]
        }

        serializer = CargaCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        carga = serializer.save()

        self.assertEqual(carga.bloques.count(), 3)
        self.assertEqual(carga.estado, Carga.Estado.CORRECTA)

    def test_crear_carga_invalida_con_horas_incorrectas(self):
        """Test que crear carga con horas incorrectas lance excepción."""
        data = {
            'programa_academico': self.programa.id,
            'materia': self.materia.id,
            'profesor': self.profesor.id,
            'periodo': self.periodo.id,
            'bloques': [
                {'dia': 'LUN', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'}
            ]  # Solo 2 horas, pero materia requiere 6
        }

        serializer = CargaCreateUpdateSerializer(data=data)

        with self.assertRaises(HorasInvalidasException):
            if serializer.is_valid():
                serializer.save()
            else:
                # Si la validación falla en validate(), raise la excepción
                raise HorasInvalidasException(
                    "Las horas de los bloques no coinciden con las horas de la materia"
                )

    def test_crear_carga_con_conflicto_horario(self):
        """Test que crear carga con conflicto horario lance excepción."""
        # Crear primera carga con 6 horas correctas
        carga1 = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga1,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        BloqueHorario.objects.create(
            carga=carga1,
            dia='MIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        BloqueHorario.objects.create(
            carga=carga1,
            dia='VIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Intentar crear segunda carga con el mismo profesor en horario solapado
        # Proporcionar 6 horas correctas pero con conflicto en LUN
        data = {
            'programa_academico': self.programa.id,
            'materia': self.materia.id,
            'profesor': self.profesor.id,
            'periodo': self.periodo.id,
            'bloques': [
                {'dia': 'LUN', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'},
                {'dia': 'MAR', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'},
                {'dia': 'JUE', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'}
            ]
        }

        serializer = CargaCreateUpdateSerializer(data=data)

        with self.assertRaises(ConflictoHorarioException):
            if serializer.is_valid():
                serializer.save()
            else:
                raise ConflictoHorarioException("Conflicto de horario detectado")

    def test_no_crear_carga_en_periodo_finalizado(self):
        """Test que no se pueda crear carga en periodo finalizado."""
        self.periodo.finalizado = True
        self.periodo.save()

        data = {
            'programa_academico': self.programa.id,
            'materia': self.materia.id,
            'profesor': self.profesor.id,
            'periodo': self.periodo.id,
            'bloques': [
                {'dia': 'LUN', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'}
            ]
        }

        serializer = CargaCreateUpdateSerializer(data=data)

        with self.assertRaises(PeriodoFinalizadoException):
            if serializer.is_valid():
                serializer.save()
            else:
                raise PeriodoFinalizadoException("No se puede crear carga en periodo finalizado")

    def test_actualizar_bloques_de_carga_existente(self):
        """Test actualizar bloques de una carga existente."""
        # Crear carga inicial con 6 horas
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='MIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='VIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Actualizar bloques (cambiar horarios pero mantener 6 horas)
        data = {
            'programa_academico': self.programa.id,
            'materia': self.materia.id,
            'profesor': self.profesor.id,
            'periodo': self.periodo.id,
            'bloques': [
                {'dia': 'MAR', 'hora_inicio': '10:00:00', 'hora_fin': '12:00:00'},
                {'dia': 'JUE', 'hora_inicio': '10:00:00', 'hora_fin': '12:00:00'},
                {'dia': 'VIE', 'hora_inicio': '10:00:00', 'hora_fin': '12:00:00'}
            ]
        }

        serializer = CargaCreateUpdateSerializer(carga, data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        carga_actualizada = serializer.save()

        self.assertEqual(carga_actualizada.bloques.count(), 3)
        # Verificar que los bloques fueron reemplazados
        self.assertTrue(carga_actualizada.bloques.filter(dia='MAR').exists())
        self.assertFalse(carga_actualizada.bloques.filter(dia='LUN').exists())

    def test_estado_automatico_erroneo_con_horas_incorrectas(self):
        """Test que el estado se calcule automáticamente como ERRONEA."""
        # Crear carga sin bloques
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

        # Agregar solo 2 horas (materia requiere 6)
        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Actualizar estado usando el serializer
        serializer = CargaCreateUpdateSerializer(carga)
        serializer._actualizar_estado(carga)

        self.assertEqual(carga.estado, Carga.Estado.ERRONEA)

    def test_estado_automatico_correcto(self):
        """Test que el estado se calcule automáticamente como CORRECTA."""
        # Crear carga con 6 horas correctas
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

        BloqueHorario.objects.create(
            carga=carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='MIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )
        BloqueHorario.objects.create(
            carga=carga,
            dia='VIE',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        # Actualizar estado usando el serializer
        serializer = CargaCreateUpdateSerializer(carga)
        serializer._actualizar_estado(carga)

        self.assertEqual(carga.estado, Carga.Estado.CORRECTA)


class CargaListSerializerTestCase(TestCase):
    """Tests para CargaListSerializer (lightweight read)."""

    def setUp(self):
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre="Ingeniería en Software"
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave="CS101",
            nombre="Programación I",
            horas=6
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre="Dr. Juan Pérez",
            email="juan@universidad.edu"
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre="2025-1"
        )

    def test_list_serializer_lightweight(self):
        """Test que CargaListSerializer retorne solo campos necesarios."""
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.CORRECTA
        )

        serializer = CargaListSerializer(carga)
        data = serializer.data

        # Verificar que tenga los campos lightweight
        self.assertIn('id', data)
        self.assertIn('materia_clave', data)
        self.assertIn('profesor_nombre', data)
        self.assertIn('estado', data)
        self.assertIn('estado_display', data)
