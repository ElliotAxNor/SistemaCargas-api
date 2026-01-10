# Sistema de Cargas Académicas - API

API REST para la gestión y asignación de cargas docentes en instituciones educativas.

## ¿Qué hace este sistema?

Gestiona la asignación de profesores a materias (cargas académicas) validando automáticamente:
- **Conflictos de horarios** entre cargas del mismo profesor
- **Horas correctas** de bloques horarios según la materia
- **Permisos por rol** (Responsable de Unidad / Responsable de Programa)

## Stack Tecnológico

- Python 3.9+
- Django 4.2+ con Django REST Framework
- SQLite
- JWT para autenticación

## Instalación Rápida

### 1. Clonar y preparar entorno

```bash
git clone https://github.com/ElliotAxNor/SistemaCargas-api.git
cd SistemaCargas-api

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crea un archivo `.env` (usa `.env.example` como referencia):

### 3. Configurar base de datos

```bash
python manage.py migrate
```

### 4. Crear datos de desarrollo (OPCIONAL pero recomendado)

Para facilitar las pruebas, ejecuta el script que crea automáticamente:
- 1 Unidad Académica
- 3 Programas Académicos
- Usuarios con diferentes roles
- 10 Profesores
- 18 Materias distribuidas
- 1 Periodo activo

```bash
python scripts/populate_dev_data.py
```

**Credenciales creadas:**
- Responsable de Unidad: `resp_unidad` / `desarrollo123`
- Responsable de Software: `resp_software` / `desarrollo123`
- Responsable de Sistemas: `resp_sistemas` / `desarrollo123`
- Responsable de Datos: `resp_datos` / `desarrollo123`

> **Nota:** Si prefieres limpiar y recrear datos: `python scripts/populate_dev_data.py --clean`

### 5. Ejecutar servidor

```bash
python manage.py runserver
```

API disponible en: **http://127.0.0.1:8000/api/**

## Uso Básico

### Autenticación

```bash
# Obtener token JWT
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "resp_software", "password": "desarrollo123"}'

# Usar el token en peticiones
curl http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer <tu-token>"
```

### Endpoints Principales

- `/api/core/unidades-academicas/` - Unidades académicas
- `/api/core/programas-academicos/` - Programas académicos
- `/api/academico/profesores/` - Profesores
- `/api/academico/materias/` - Materias
- `/api/asignaciones/periodos/` - Periodos académicos
- `/api/asignaciones/cargas/` - Cargas (asignaciones profesor-materia)
- `/api/asignaciones/bloques-horarios/` - Bloques horarios

**Ver documentación completa en:** `ENDPOINTS.md`

## Arquitectura

El proyecto sigue el patrón **Fat Services, Thin Models**:

- **Models:** Solo estructura de datos, sin lógica de negocio
- **Services:** Toda la lógica de validación y reglas de negocio
  - `ValidadorConflictos` - Detecta solapamiento de horarios
  - `ValidadorHoras` - Valida horas de bloques vs materia
  - `PeriodoService` - Gestión de periodos y estadísticas
- **Serializers:** Transformación y validación de datos
- **ViewSets:** Manejo de peticiones HTTP

## Testing

```bash
# Ejecutar todos los tests (54 tests)
python manage.py test

# Tests específicos
python manage.py test apps.asignaciones.tests.test_services
```

## Estructura de Carpetas

```
SistemaCargas-api/
├── apps/
│   ├── core/              # Unidades, Programas, Usuarios
│   ├── academico/         # Profesores, Materias
│   └── asignaciones/      # Periodos, Cargas, Bloques
│       ├── services/      # Lógica de negocio
│       └── tests/         # Suite de tests
├── common/                # Utilidades (permisos, excepciones)
├── config/                # Configuración Django
├── scripts/               # Scripts de utilidad
│   └── populate_dev_data.py  # Población de datos de desarrollo
└── manage.py
```

## Documentación Adicional

- `ENDPOINTS.md` - Documentación completa de endpoints
- `SERIALIZERS.md` - Serializers y validaciones
- `CLAUDE.md` - Guía de arquitectura y desarrollo
- `QUICKSTART.md` - Guía rápida con ejemplos cURL
- `DEPLOYMENT_PYTHONANYWHERE.md` - Despliegue en PythonAnywhere

## Base de Datos

Por defecto usa **SQLite**
