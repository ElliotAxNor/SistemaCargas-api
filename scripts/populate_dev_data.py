#!/usr/bin/env python
"""
Script de Población de Datos para Desarrollo

IMPORTANTE: Este script es EXCLUSIVO para entorno de desarrollo.
NO ejecutar en producción.

Crea datos base para facilitar el desarrollo y testing:
- 1 Unidad Académica
- 3 Programas Académicos
- Usuarios con roles RESP_UNIDAD y RESP_PROGRAMA
- Profesores compartidos
- Materias por programa
- 1 Periodo activo

NO crea cargas ni bloques horarios (solo datos maestros).

Ejecución:
    python scripts/populate_dev_data.py

    # Con limpieza previa:
    python scripts/populate_dev_data.py --clean

Autor: Sistema de Cargas Académicas
"""

import os
import sys
import django
import argparse

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.core.models import UnidadAcademica, ProgramaAcademico
from apps.academico.models import Profesor, Materia
from apps.asignaciones.models import Periodo

User = get_user_model()


class Colors:
    """Colores ANSI para terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Imprime encabezado con formato"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.ENDC}")


def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def clean_database():
    """Limpia datos existentes (excepto superusuario)"""
    print_header("LIMPIANDO BASE DE DATOS")

    print_warning("Eliminando datos existentes...")

    # Eliminar en orden inverso a las dependencias
    Materia.objects.all().delete()
    print_info("Materias eliminadas")

    Profesor.objects.all().delete()
    print_info("Profesores eliminados")

    Periodo.objects.all().delete()
    print_info("Periodos eliminados")

    ProgramaAcademico.objects.all().delete()
    print_info("Programas Académicos eliminados")

    UnidadAcademica.objects.all().delete()
    print_info("Unidades Académicas eliminadas")

    # Eliminar usuarios no superusuarios
    User.objects.filter(is_superuser=False).delete()
    print_info("Usuarios (no superusuarios) eliminados")

    print_success("Base de datos limpiada exitosamente\n")


def create_unidad_academica():
    """Crea la Unidad Académica principal"""
    print_header("CREANDO UNIDAD ACADÉMICA")

    unidad, created = UnidadAcademica.objects.get_or_create(
        nombre="Facultad de Ingeniería y Ciencias",
        defaults={}
    )

    if created:
        print_success(f"Unidad Académica creada: {unidad.nombre}")
    else:
        print_info(f"Unidad Académica ya existía: {unidad.nombre}")

    return unidad


def create_programas_academicos(unidad):
    """Crea Programas Académicos"""
    print_header("CREANDO PROGRAMAS ACADÉMICOS")

    programas_data = [
        {"nombre": "Ingeniería en Software"},
        {"nombre": "Ingeniería en Sistemas Computacionales"},
        {"nombre": "Ingeniería en Ciencias de Datos"},
    ]

    programas = []
    for data in programas_data:
        programa, created = ProgramaAcademico.objects.get_or_create(
            unidad_academica=unidad,
            nombre=data["nombre"],
            defaults={}
        )
        programas.append(programa)

        if created:
            print_success(f"Programa creado: {programa.nombre}")
        else:
            print_info(f"Programa ya existía: {programa.nombre}")

    return programas


def create_usuarios(unidad, programas):
    """Crea usuarios con roles"""
    print_header("CREANDO USUARIOS")

    usuarios_creados = []

    # 1. Responsable de Unidad
    resp_unidad, created = User.objects.get_or_create(
        username="resp_unidad",
        defaults={
            "email": "resp.unidad@universidad.edu",
            "first_name": "María",
            "last_name": "González",
            "rol": "RESP_UNIDAD",
            "unidad_academica": unidad,
        }
    )
    if created:
        resp_unidad.set_password("desarrollo123")
        resp_unidad.save()
        print_success(f"Usuario creado: {resp_unidad.username} (RESP_UNIDAD)")
        print_info(f"  → Email: {resp_unidad.email}")
        print_info(f"  → Password: desarrollo123")
    else:
        print_info(f"Usuario ya existía: {resp_unidad.username}")

    usuarios_creados.append(resp_unidad)

    # 2. Responsables de Programa
    responsables_data = [
        {
            "username": "resp_software",
            "email": "resp.software@universidad.edu",
            "first_name": "Juan",
            "last_name": "Pérez",
            "programa": programas[0],
        },
        {
            "username": "resp_sistemas",
            "email": "resp.sistemas@universidad.edu",
            "first_name": "Ana",
            "last_name": "Martínez",
            "programa": programas[1],
        },
        {
            "username": "resp_datos",
            "email": "resp.datos@universidad.edu",
            "first_name": "Carlos",
            "last_name": "López",
            "programa": programas[2],
        },
    ]

    for data in responsables_data:
        usuario, created = User.objects.get_or_create(
            username=data["username"],
            defaults={
                "email": data["email"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "rol": "RESP_PROGRAMA",
                "programa_academico": data["programa"],
            }
        )
        if created:
            usuario.set_password("desarrollo123")
            usuario.save()
            print_success(f"Usuario creado: {usuario.username} (RESP_PROGRAMA)")
            print_info(f"  → Email: {usuario.email}")
            print_info(f"  → Programa: {data['programa'].nombre}")
            print_info(f"  → Password: desarrollo123")
        else:
            print_info(f"Usuario ya existía: {usuario.username}")

        usuarios_creados.append(usuario)

    return usuarios_creados


def create_profesores(unidad):
    """Crea profesores compartidos de la unidad"""
    print_header("CREANDO PROFESORES")

    profesores_data = [
        {"nombre": "Dr. Roberto Sánchez", "email": "roberto.sanchez@universidad.edu"},
        {"nombre": "Dra. Laura Fernández", "email": "laura.fernandez@universidad.edu"},
        {"nombre": "M.C. José Ramírez", "email": "jose.ramirez@universidad.edu"},
        {"nombre": "Dr. Patricia Torres", "email": "patricia.torres@universidad.edu"},
        {"nombre": "M.C. Miguel Ángel Ruiz", "email": "miguel.ruiz@universidad.edu"},
        {"nombre": "Dra. Carmen Díaz", "email": "carmen.diaz@universidad.edu"},
        {"nombre": "Dr. Fernando Castro", "email": "fernando.castro@universidad.edu"},
        {"nombre": "M.C. Sofía Morales", "email": "sofia.morales@universidad.edu"},
        {"nombre": "Dr. Alberto Jiménez", "email": "alberto.jimenez@universidad.edu"},
        {"nombre": "Dra. Isabel Romero", "email": "isabel.romero@universidad.edu"},
    ]

    profesores = []
    for data in profesores_data:
        profesor, created = Profesor.objects.get_or_create(
            unidad_academica=unidad,
            email=data["email"],
            defaults={"nombre": data["nombre"]}
        )
        profesores.append(profesor)

        if created:
            print_success(f"Profesor creado: {profesor.nombre}")
        else:
            print_info(f"Profesor ya existía: {profesor.nombre}")

    return profesores


def create_materias(programas):
    """Crea materias para cada programa"""
    print_header("CREANDO MATERIAS")

    # Materias por programa
    materias_por_programa = {
        "Ingeniería en Software": [
            {"clave": "SW101", "nombre": "Fundamentos de Programación", "horas": 6},
            {"clave": "SW102", "nombre": "Estructuras de Datos", "horas": 6},
            {"clave": "SW201", "nombre": "Programación Orientada a Objetos", "horas": 6},
            {"clave": "SW202", "nombre": "Bases de Datos", "horas": 6},
            {"clave": "SW301", "nombre": "Ingeniería de Software", "horas": 4},
            {"clave": "SW302", "nombre": "Arquitectura de Software", "horas": 4},
        ],
        "Ingeniería en Sistemas Computacionales": [
            {"clave": "SC101", "nombre": "Introducción a la Computación", "horas": 6},
            {"clave": "SC102", "nombre": "Matemáticas Discretas", "horas": 6},
            {"clave": "SC201", "nombre": "Sistemas Operativos", "horas": 6},
            {"clave": "SC202", "nombre": "Redes de Computadoras", "horas": 6},
            {"clave": "SC301", "nombre": "Seguridad Informática", "horas": 4},
            {"clave": "SC302", "nombre": "Administración de Sistemas", "horas": 4},
        ],
        "Ingeniería en Ciencias de Datos": [
            {"clave": "CD101", "nombre": "Introducción a Data Science", "horas": 6},
            {"clave": "CD102", "nombre": "Estadística para Datos", "horas": 6},
            {"clave": "CD201", "nombre": "Machine Learning I", "horas": 6},
            {"clave": "CD202", "nombre": "Visualización de Datos", "horas": 4},
            {"clave": "CD301", "nombre": "Deep Learning", "horas": 6},
            {"clave": "CD302", "nombre": "Big Data Analytics", "horas": 4},
        ],
    }

    materias_creadas = []
    for programa in programas:
        materias_data = materias_por_programa.get(programa.nombre, [])

        print(f"\n{Colors.CYAN}Programa: {programa.nombre}{Colors.ENDC}")

        for data in materias_data:
            materia, created = Materia.objects.get_or_create(
                programa_academico=programa,
                clave=data["clave"],
                defaults={
                    "nombre": data["nombre"],
                    "horas": data["horas"]
                }
            )
            materias_creadas.append(materia)

            if created:
                print_success(f"  Materia creada: {materia.clave} - {materia.nombre} ({materia.horas}h)")
            else:
                print_info(f"  Materia ya existía: {materia.clave}")

    return materias_creadas


def create_periodo(unidad):
    """Crea un periodo académico activo"""
    print_header("CREANDO PERIODO ACADÉMICO")

    periodo, created = Periodo.objects.get_or_create(
        unidad_academica=unidad,
        nombre="2025-1",
        defaults={"finalizado": False}
    )

    if created:
        print_success(f"Periodo creado: {periodo.nombre} (Activo)")
    else:
        print_info(f"Periodo ya existía: {periodo.nombre}")

    return periodo


def print_summary(unidad, programas, usuarios, profesores, materias, periodo):
    """Imprime resumen de datos creados"""
    print_header("RESUMEN DE DATOS CREADOS")

    print(f"{Colors.BOLD}Unidad Académica:{Colors.ENDC}")
    print(f"  • {unidad.nombre} (ID: {unidad.id})")

    print(f"\n{Colors.BOLD}Programas Académicos: {len(programas)}{Colors.ENDC}")
    for programa in programas:
        print(f"  • {programa.nombre} (ID: {programa.id})")

    print(f"\n{Colors.BOLD}Usuarios: {len(usuarios)}{Colors.ENDC}")
    for usuario in usuarios:
        rol_display = "RESP. UNIDAD" if usuario.rol == "RESP_UNIDAD" else "RESP. PROGRAMA"
        print(f"  • {usuario.username} - {usuario.get_full_name()} ({rol_display})")

    print(f"\n{Colors.BOLD}Profesores: {len(profesores)}{Colors.ENDC}")
    for profesor in profesores:
        print(f"  • {profesor.nombre}")

    print(f"\n{Colors.BOLD}Materias: {len(materias)}{Colors.ENDC}")
    print(f"  • Total: {len(materias)} materias distribuidas en {len(programas)} programas")

    print(f"\n{Colors.BOLD}Periodo Académico:{Colors.ENDC}")
    print(f"  • {periodo.nombre} (Activo)")

    print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.GREEN}{Colors.BOLD}DATOS DE DESARROLLO CREADOS EXITOSAMENTE{Colors.ENDC}")
    print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

    print(f"{Colors.CYAN}Credenciales de acceso:{Colors.ENDC}")
    print(f"  Usuario Admin: admin / admin123")
    print(f"  Resp. Unidad: resp_unidad / desarrollo123")
    print(f"  Resp. Software: resp_software / desarrollo123")
    print(f"  Resp. Sistemas: resp_sistemas / desarrollo123")
    print(f"  Resp. Datos: resp_datos / desarrollo123")

    print(f"\n{Colors.YELLOW}Siguiente paso:{Colors.ENDC}")
    print(f"  Ejecutar el servidor: python manage.py runserver")
    print(f"  API Base: http://127.0.0.1:8000/api/")
    print(f"  Admin: http://127.0.0.1:8000/admin/\n")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Población de datos para desarrollo del Sistema de Cargas Académicas'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Limpiar datos existentes antes de crear nuevos'
    )

    args = parser.parse_args()

    print_header("SCRIPT DE POBLACIÓN DE DATOS PARA DESARROLLO")
    print_warning("Este script es EXCLUSIVO para entorno de desarrollo")
    print_warning("NO ejecutar en producción\n")

    try:
        # Limpieza opcional
        if args.clean:
            clean_database()

        # Crear datos
        unidad = create_unidad_academica()
        programas = create_programas_academicos(unidad)
        usuarios = create_usuarios(unidad, programas)
        profesores = create_profesores(unidad)
        materias = create_materias(programas)
        periodo = create_periodo(unidad)

        # Resumen
        print_summary(unidad, programas, usuarios, profesores, materias, periodo)

    except Exception as e:
        print_error(f"Error al crear datos: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
