"""
Tests para ViewSets del módulo Asignaciones (API Endpoints).
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import time

from apps.core.models import UnidadAcademica, ProgramaAcademico
from apps.academico.models import Profesor, Materia
from apps.asignaciones.models import Periodo, Carga, BloqueHorario

User = get_user_model()


class PeriodoViewSetTestCase(TestCase):
    """Tests para PeriodoViewSet endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")

        # Crear usuario con autenticación
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            rol=User.Rol.RESP_UNIDAD,
            unidad_academica=self.unidad
        )
        self.client.force_authenticate(user=self.user)

    def test_listar_periodos(self):
        """Test GET /api/asignaciones/periodos/"""
        Periodo.objects.create(unidad_academica=self.unidad, nombre='2025-1')
        Periodo.objects.create(unidad_academica=self.unidad, nombre='2025-2')

        response = self.client.get('/api/asignaciones/periodos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_crear_periodo(self):
        """Test POST /api/asignaciones/periodos/"""
        data = {
            'unidad_academica': self.unidad.id,
            'nombre': '2025-1'
        }

        response = self.client.post('/api/asignaciones/periodos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], '2025-1')
        self.assertFalse(response.data['finalizado'])

    def test_obtener_detalle_periodo(self):
        """Test GET /api/asignaciones/periodos/{id}/"""
        periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )

        response = self.client.get(f'/api/asignaciones/periodos/{periodo.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], '2025-1')

    def test_actualizar_periodo(self):
        """Test PUT /api/asignaciones/periodos/{id}/"""
        periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )

        data = {
            'unidad_academica': self.unidad.id,
            'nombre': '2025-1 Actualizado'
        }

        response = self.client.put(f'/api/asignaciones/periodos/{periodo.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], '2025-1 Actualizado')

    def test_eliminar_periodo(self):
        """Test DELETE /api/asignaciones/periodos/{id}/"""
        periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )

        response = self.client.delete(f'/api/asignaciones/periodos/{periodo.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Periodo.objects.filter(id=periodo.id).exists())

    def test_finalizar_periodo_sin_cargas(self):
        """Test POST /api/asignaciones/periodos/{id}/finalizar/ - sin cargas."""
        periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )

        response = self.client.post(f'/api/asignaciones/periodos/{periodo.id}/finalizar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)
        self.assertIn('periodo', response.data)

        periodo.refresh_from_db()
        self.assertTrue(periodo.finalizado)

    def test_finalizar_periodo_con_cargas_problematicas(self):
        """Test POST /api/asignaciones/periodos/{id}/finalizar/ - con cargas problemáticas."""
        periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )
        programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre='Ing. Software'
        )
        materia = Materia.objects.create(
            programa_academico=programa,
            clave='CS101',
            nombre='Programación',
            horas=6
        )
        profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre='Dr. Juan',
            email='juan@test.com'
        )

        # Crear carga pendiente (sin bloques)
        Carga.objects.create(
            programa_academico=programa,
            materia=materia,
            profesor=profesor,
            periodo=periodo,
            estado=Carga.Estado.PENDIENTE
        )

        response = self.client.post(f'/api/asignaciones/periodos/{periodo.id}/finalizar/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])

    def test_obtener_estadisticas_periodo(self):
        """Test GET /api/asignaciones/periodos/{id}/estadisticas/"""
        periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )

        response = self.client.get(f'/api/asignaciones/periodos/{periodo.id}/estadisticas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_cargas', response.data)
        self.assertIn('cargas_por_estado', response.data)
        self.assertIn('correctas', response.data['cargas_por_estado'])
        self.assertIn('pendientes', response.data['cargas_por_estado'])

    def test_obtener_cargas_problematicas(self):
        """Test GET /api/asignaciones/periodos/{id}/cargas_problematicas/"""
        periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )

        response = self.client.get(f'/api/asignaciones/periodos/{periodo.id}/cargas_problematicas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_pendientes', response.data)
        self.assertIn('pendientes', response.data)


class CargaViewSetTestCase(TestCase):
    """Tests para CargaViewSet endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre='Ing. Software'
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave='CS101',
            nombre='Programación I',
            horas=6
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre='Dr. Juan Pérez',
            email='juan@test.com'
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )

        # Crear usuario autenticado
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            rol=User.Rol.RESP_PROGRAMA,
            programa_academico=self.programa
        )
        self.client.force_authenticate(user=self.user)

    def test_listar_cargas(self):
        """Test GET /api/asignaciones/cargas/"""
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

        response = self.client.get('/api/asignaciones/cargas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_crear_carga_valida(self):
        """Test POST /api/asignaciones/cargas/ - carga válida con horas correctas."""
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

        response = self.client.post('/api/asignaciones/cargas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['estado'], 'CORRECTA')

    def test_crear_carga_con_horas_incorrectas(self):
        """Test POST /api/asignaciones/cargas/ - horas incorrectas (error 400)."""
        data = {
            'programa_academico': self.programa.id,
            'materia': self.materia.id,
            'profesor': self.profesor.id,
            'periodo': self.periodo.id,
            'bloques': [
                {'dia': 'LUN', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'}
            ]  # Solo 2 horas, materia requiere 6
        }

        response = self.client.post('/api/asignaciones/cargas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_crear_carga_con_conflicto_horario(self):
        """Test POST /api/asignaciones/cargas/ - conflicto de horario (error 409)."""
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

        # Intentar crear segunda carga con conflicto (6 horas pero con solapamiento en LUN)
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

        response = self.client.post('/api/asignaciones/cargas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_validar_disponibilidad_profesor_disponible(self):
        """Test POST /api/asignaciones/cargas/validar_disponibilidad/ - profesor disponible."""
        data = {
            'profesor_id': self.profesor.id,
            'periodo_id': self.periodo.id,
            'bloques': [
                {'dia': 'LUN', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'}
            ]
        }

        response = self.client.post(
            '/api/asignaciones/cargas/validar_disponibilidad/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['disponible'])

    def test_validar_disponibilidad_profesor_ocupado(self):
        """Test POST /api/asignaciones/cargas/validar_disponibilidad/ - profesor ocupado."""
        # Crear carga existente
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

        # Validar disponibilidad en el mismo horario
        data = {
            'profesor_id': self.profesor.id,
            'periodo_id': self.periodo.id,
            'bloques': [
                {'dia': 'LUN', 'hora_inicio': '08:00:00', 'hora_fin': '10:00:00'}
            ]
        }

        response = self.client.post(
            '/api/asignaciones/cargas/validar_disponibilidad/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(response.data['disponible'])

    def test_validar_carga_existente(self):
        """Test GET /api/asignaciones/cargas/{id}/validar/ - validar carga existente."""
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

        response = self.client.get(f'/api/asignaciones/cargas/{carga.id}/validar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('validaciones', response.data)
        self.assertTrue(response.data['validaciones']['horas']['valida'])

    def test_obtener_cargas_por_estado(self):
        """Test GET /api/asignaciones/cargas/por_estado/?periodo=1"""
        # Crear cargas con diferentes estados
        carga_correcta = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.CORRECTA
        )
        carga_pendiente = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo,
            estado=Carga.Estado.PENDIENTE
        )

        response = self.client.get(
            f'/api/asignaciones/cargas/por_estado/?periodo={self.periodo.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('correctas', response.data)
        self.assertIn('pendientes', response.data)

    def test_filtrar_cargas_por_periodo(self):
        """Test GET /api/asignaciones/cargas/?periodo=1"""
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

        # Crear otro periodo y carga
        periodo2 = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-2'
        )
        Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=periodo2
        )

        response = self.client.get(f'/api/asignaciones/cargas/?periodo={self.periodo.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_actualizar_carga(self):
        """Test PUT /api/asignaciones/cargas/{id}/ - actualizar bloques."""
        carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

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

        response = self.client.put(
            f'/api/asignaciones/cargas/{carga.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(carga.bloques.count(), 3)


class CargaViewSetAuthenticationTestCase(TestCase):
    """Tests para autenticación en CargaViewSet."""

    def setUp(self):
        self.client = APIClient()
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")

    def test_listar_cargas_sin_autenticacion(self):
        """Test GET /api/asignaciones/cargas/ sin autenticación (401)."""
        response = self.client.get('/api/asignaciones/cargas/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_carga_sin_autenticacion(self):
        """Test POST /api/asignaciones/cargas/ sin autenticación (401)."""
        data = {
            'programa_academico': 1,
            'materia': 1,
            'profesor': 1,
            'periodo': 1
        }

        response = self.client.post('/api/asignaciones/cargas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BloqueHorarioViewSetTestCase(TestCase):
    """Tests para BloqueHorarioViewSet (read-only)."""

    def setUp(self):
        self.client = APIClient()
        self.unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")
        self.programa = ProgramaAcademico.objects.create(
            unidad_academica=self.unidad,
            nombre='Ing. Software'
        )
        self.materia = Materia.objects.create(
            programa_academico=self.programa,
            clave='CS101',
            nombre='Programación',
            horas=6
        )
        self.profesor = Profesor.objects.create(
            unidad_academica=self.unidad,
            nombre='Dr. Juan',
            email='juan@test.com'
        )
        self.periodo = Periodo.objects.create(
            unidad_academica=self.unidad,
            nombre='2025-1'
        )
        self.carga = Carga.objects.create(
            programa_academico=self.programa,
            materia=self.materia,
            profesor=self.profesor,
            periodo=self.periodo
        )

        # Autenticar
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_listar_bloques(self):
        """Test GET /api/asignaciones/bloques-horarios/"""
        BloqueHorario.objects.create(
            carga=self.carga,
            dia='LUN',
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0)
        )

        response = self.client.get('/api/asignaciones/bloques-horarios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_crear_bloque_no_permitido(self):
        """Test POST /api/asignaciones/bloques-horarios/ no permitido (405)."""
        data = {
            'carga': self.carga.id,
            'dia': 'LUN',
            'hora_inicio': '08:00:00',
            'hora_fin': '10:00:00'
        }

        response = self.client.post('/api/asignaciones/bloques-horarios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
