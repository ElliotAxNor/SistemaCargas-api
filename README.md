# Sistema de Cargas Académicas - API Backend

API REST desarrollada con Django REST Framework para la gestión de asignación de cargas docentes en instituciones educativas.

## 📋 Descripción del Sistema

El Sistema de Cargas Académicas permite gestionar la asignación de profesores a materias (cargas académicas) en diferentes programas educativos dentro de una institución. El sistema valida automáticamente que:

- ✅ No haya conflictos de horarios entre las cargas de un mismo profesor
- ✅ Las horas asignadas en bloques horarios coincidan con las horas requeridas de la materia
- ✅ Los responsables solo gestionen recursos de su unidad o programa académico

### Características Principales

- 🔐 **Autenticación JWT** - Sistema de tokens seguro
- 👥 **Gestión de Roles** - Responsable de Unidad y Responsable de Programa
- 🏫 **Unidades y Programas Académicos** - Organización jerárquica
- 👨‍🏫 **Gestión de Profesores** - CRUD completo con asignación a unidades
- 📚 **Gestión de Materias** - Materias con horas definidas por programa
- 📅 **Periodos Académicos** - Manejo de semestres/cuatrimestres
- ✅ **Asignación de Cargas** - Asignación profesor-materia con validación
- ⏰ **Bloques Horarios** - Definición de días y horas específicas
- 🚫 **Detección de Conflictos** - Validación automática de solapamiento
- 📊 **Estadísticas** - Dashboard con métricas por unidad y programa

### Estados de Cargas

- **PENDIENTE** - Carga sin profesor asignado o sin bloques horarios
- **CORRECTA** - Carga completa con profesor y bloques horarios

## 🛠️ Stack Tecnológico

- **Python 3.9+**
- **Django 4.2+** - Framework web
- **Django REST Framework 3.14+** - API REST
- **SQLite** (desarrollo) / **PostgreSQL** (producción)
- **djangorestframework-simplejwt** - Autenticación JWT
- **django-cors-headers** - Configuración CORS
- **django-filter** - Filtrado de datos
- **python-decouple** - Variables de entorno

## 📦 Instalación y Configuración

### Prerrequisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/TU-USUARIO/SistemaCargas-api.git
cd SistemaCargas-api
```

### 2. Crear y Activar Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto (hay un `.env.example` como referencia):

```env
# Django Settings
SECRET_KEY=tu-secret-key-aqui
DJANGO_SETTINGS_MODULE=config.settings.development

# CORS - Ajusta según la URL de tu frontend
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Hosts permitidos
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de datos (opcional, por defecto usa SQLite)
# Para PostgreSQL, descomenta y configura:
# DB_NAME=sistema_cargas_db
# DB_USER=postgres
# DB_PASSWORD=tu-password
# DB_HOST=localhost
# DB_PORT=5432
```

**Para generar un SECRET_KEY seguro:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Aplicar Migraciones

```bash
python manage.py migrate
```

Esto creará todas las tablas necesarias en la base de datos.

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador:
- **Username:** (elige uno)
- **Email:** (tu email)
- **Password:** (una contraseña segura)

### 7. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

La API estará disponible en: **http://127.0.0.1:8000/**

## 🚀 Uso del Sistema

### Acceder al Panel de Administración

Abre tu navegador en: **http://127.0.0.1:8000/admin/**

Aquí podrás:
- Crear unidades académicas
- Crear programas académicos
- Registrar profesores y materias
- Crear periodos académicos
- Gestionar usuarios y roles

### Endpoints de la API

**Base URL:** `http://127.0.0.1:8000/api/`

#### Autenticación

```bash
# Obtener token
POST /api/token/
Body: {
  "username": "tu-usuario",
  "password": "tu-password"
}

# Refrescar token
POST /api/token/refresh/
Body: {
  "refresh": "tu-refresh-token"
}
```

#### Endpoints Principales

**Core (Estructura Organizacional):**
- `GET /api/core/unidades-academicas/` - Listar unidades
- `GET /api/core/programas-academicos/` - Listar programas
- `GET /api/core/usuarios/` - Listar usuarios

**Académico (Profesores y Materias):**
- `GET /api/academico/profesores/` - Listar profesores
- `GET /api/academico/materias/` - Listar materias

**Asignaciones (Cargas y Horarios):**
- `GET /api/asignaciones/periodos/` - Listar periodos
- `GET /api/asignaciones/cargas/` - Listar cargas académicas
- `GET /api/asignaciones/bloques-horarios/` - Listar bloques horarios

Ver documentación completa en **`ENDPOINTS.md`**

### Ejemplo de Uso con cURL

```bash
# 1. Obtener token
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "tu-password"}' \
  | jq -r '.access')

# 2. Listar cargas académicas
curl http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer $TOKEN"

# 3. Crear una nueva carga
curl -X POST http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profesor": 1,
    "materia": 1,
    "periodo": 1,
    "bloques_horarios": [
      {
        "dia": "LUNES",
        "hora_inicio": "08:00:00",
        "hora_fin": "10:00:00"
      }
    ]
  }'
```

## 🗂️ Estructura del Proyecto

```
SistemaCargas-api/
├── apps/
│   ├── core/              # Unidades, Programas, Usuarios
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── academico/         # Profesores y Materias
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── asignaciones/      # Periodos, Cargas, Bloques
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── services/      # Lógica de negocio
│       │   ├── validador_conflictos.py
│       │   ├── validador_horas.py
│       │   └── periodo_service.py
│       └── tests/         # Suite de pruebas
│           ├── test_services.py
│           ├── test_serializers.py
│           └── test_views.py
├── common/                # Utilidades compartidas
│   ├── exceptions.py      # Excepciones personalizadas
│   ├── pagination.py      # Paginación
│   └── permissions.py     # Permisos por rol
├── config/
│   ├── settings/
│   │   ├── base.py        # Settings compartidos
│   │   ├── development.py # Configuración desarrollo
│   │   └── production.py  # Configuración producción
│   ├── urls.py            # URLs principales
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🏗️ Arquitectura: Fat Services, Thin Models

El proyecto sigue el principio de **separación de responsabilidades**:

### Modelos (Datos)
Los modelos Django son simples y solo contienen:
- Estructura de datos (campos)
- Relaciones entre modelos
- Método `__str__()`

**NO contienen lógica de negocio.**

### Services (Lógica de Negocio)
La validación y lógica compleja está en `apps/asignaciones/services/`:

**ValidadorConflictos:**
- Detecta solapamiento de horarios
- Previene conflictos de asignación de profesores

**ValidadorHoras:**
- Valida que las horas de bloques coincidan con horas de materia

**PeriodoService:**
- Gestiona finalización de periodos
- Genera estadísticas

Ver `apps/asignaciones/services/README.md` para más detalles.

### Serializers (Validación y Transformación)
Los serializers integran los services para validar automáticamente al crear/actualizar cargas.

### ViewSets (API HTTP)
Los viewsets manejan requests HTTP y delegan la lógica a serializers y services.

## 🧪 Testing

El proyecto incluye una suite completa de 54 tests.

### Ejecutar Todos los Tests

```bash
python manage.py test
```

### Ejecutar Tests Específicos

```bash
# Por app
python manage.py test apps.asignaciones

# Por archivo
python manage.py test apps.asignaciones.tests.test_services

# Test específico
python manage.py test apps.asignaciones.tests.test_services.ValidadorConflictosTestCase.test_bloques_se_solapan_mismo_dia

# Con más detalle
python manage.py test --verbosity=2
```

## 🗄️ Base de Datos

### SQLite (Por Defecto)

El proyecto usa SQLite por defecto, ideal para desarrollo:
- No requiere instalación adicional
- Base de datos en archivo `db.sqlite3`
- Perfecta para desarrollo local

### PostgreSQL (Opcional)

Para usar PostgreSQL en desarrollo:

1. **Instalar PostgreSQL** en tu sistema

2. **Crear base de datos:**
```sql
CREATE DATABASE sistema_cargas_db;
```

3. **Instalar driver:**
```bash
pip install psycopg2-binary
```

4. **Configurar `.env`:**
```env
DB_NAME=sistema_cargas_db
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432
```

5. **Descomentar** configuración PostgreSQL en `config/settings/development.py`

6. **Ejecutar migraciones:**
```bash
python manage.py migrate
```

## 📊 Crear Datos de Prueba

### Opción 1: Admin de Django

Usa el panel de administración en `/admin/` para crear datos manualmente.

### Opción 2: Django Shell

```bash
python manage.py shell
```

```python
from apps.core.models import UnidadAcademica, ProgramaAcademico
from apps.academico.models import Profesor, Materia
from apps.asignaciones.models import Periodo

# Crear unidad académica
unidad = UnidadAcademica.objects.create(
    nombre="Facultad de Ingeniería"
)

# Crear programa académico
programa = ProgramaAcademico.objects.create(
    nombre="Ingeniería en Software",
    unidad_academica=unidad
)

# Crear periodo
periodo = Periodo.objects.create(
    nombre="2025-1",
    unidad_academica=unidad
)

# Crear profesor
profesor = Profesor.objects.create(
    nombre="Dr. Juan Pérez",
    email="juan.perez@universidad.edu",
    unidad_academica=unidad
)

# Crear materia
materia = Materia.objects.create(
    clave="CS101",
    nombre="Programación I",
    horas=6,
    programa_academico=programa
)

print("✅ Datos de prueba creados!")
```

## 🚀 Despliegue en Producción

### PythonAnywhere

Para desplegar en PythonAnywhere, consulta **`DEPLOYMENT_PYTHONANYWHERE.md`**.

Características:
- ✅ SQLite funciona perfectamente (datos persistentes)
- ✅ Completamente gratis
- ✅ Ideal para proyectos académicos

### Render.com

Para desplegar en Render.com, consulta **`DEPLOYMENT.md`**.

Recomendado si necesitas PostgreSQL gratis.

### Consideraciones de Producción

Antes de desplegar:

1. ✅ Cambiar `DEBUG = False` en production.py
2. ✅ Configurar `ALLOWED_HOSTS` con tu dominio
3. ✅ Configurar `CORS_ALLOWED_ORIGINS` con URL de frontend
4. ✅ Usar PostgreSQL en lugar de SQLite
5. ✅ Configurar SECRET_KEY seguro en variables de entorno
6. ✅ Ejecutar `collectstatic` para archivos estáticos
7. ✅ Configurar HTTPS

## 📚 Documentación Adicional

- **`ENDPOINTS.md`** - Documentación completa de todos los endpoints
- **`SERIALIZERS.md`** - Documentación de serializers y validaciones
- **`CLAUDE.md`** - Guía de desarrollo y arquitectura
- **`QUICKSTART.md`** - Guía rápida de pruebas con curl
- **`DEPLOYMENT_PYTHONANYWHERE.md`** - Despliegue en PythonAnywhere
- **`DEPLOYMENT.md`** - Despliegue en Render.com

## 🛠️ Comandos Útiles

```bash
# Desarrollo
python manage.py runserver          # Iniciar servidor
python manage.py shell               # Shell interactivo de Django
python manage.py createsuperuser     # Crear administrador

# Base de datos
python manage.py makemigrations      # Crear migraciones
python manage.py migrate             # Aplicar migraciones
python manage.py showmigrations      # Ver estado de migraciones

# Testing
python manage.py test                # Ejecutar todos los tests
python manage.py test apps.core      # Tests de una app específica

# Producción
python manage.py collectstatic       # Recolectar archivos estáticos
python manage.py check --deploy      # Verificar configuración de producción
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de uso académico.

## 👥 Autores

Desarrollado como proyecto académico.

## 🆘 Soporte y Problemas

Si encuentras problemas:

1. Revisa los logs del servidor
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que las migraciones estén aplicadas
4. Consulta la documentación en archivos `.md`
5. Revisa `CLAUDE.md` para entender la arquitectura

## ✅ Estado del Proyecto

- ✅ Backend API completo y funcional
- ✅ Autenticación JWT implementada
- ✅ CRUD completo de todas las entidades
- ✅ Validación automática de conflictos de horario
- ✅ Validación automática de horas
- ✅ Sistema de roles y permisos
- ✅ Suite completa de 54 tests (100% passing)
- ✅ Documentación completa
- ✅ Frontend React integrado

---

**Versión:** 1.0.0
**Última actualización:** Enero 2026
**Python:** 3.9+
**Django:** 4.2+
