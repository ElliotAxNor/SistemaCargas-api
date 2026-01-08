# Sistema de Cargas Académicas - API REST

API REST construida con Django REST Framework para gestionar asignaciones de profesores a materias, previniendo conflictos de horarios.

## Stack Tecnológico

- **Django 4.2** - Framework web
- **Django REST Framework** - API REST
- **SQLite** - Base de datos (por defecto)
- **JWT (SimpleJWT)** - Autenticación
- **CORS Headers** - Cross-Origin Resource Sharing
- **Django Filter** - Filtrado de datos

## Instalación

### 1. Clonar el repositorio

```bash
cd SistemaCargas-api
```

### 2. Crear entorno virtual y activarlo

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

### 6. Ejecutar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## Credenciales de Admin (Pre-creadas)

- **Usuario:** admin
- **Contraseña:** admin123
- **URL Admin:** http://127.0.0.1:8000/admin/

## Endpoints Principales

### Autenticación (JWT)

```bash
POST /api/token/          # Obtener access y refresh token
POST /api/token/refresh/  # Refrescar access token
```

**Ejemplo:**
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Apps

```
/api/core/         # UnidadAcademica, ProgramaAcademico, Usuario
/api/academico/    # Profesor, Materia
/api/asignaciones/ # Periodo, Carga, BloqueHorario
```

## Estructura del Proyecto

```
SistemaCargas-api/
├── apps/
│   ├── core/              # Modelos: UnidadAcademica, ProgramaAcademico, Usuario
│   ├── academico/         # Modelos: Profesor, Materia
│   └── asignaciones/      # Modelos: Periodo, Carga, BloqueHorario
│       └── services/      # Lógica de negocio
│           ├── validador_conflictos.py
│           ├── validador_horas.py
│           └── periodo_service.py
├── common/                # Utilidades compartidas
│   ├── exceptions.py      # Excepciones personalizadas
│   ├── pagination.py      # Paginación
│   └── permissions.py     # Permisos por rol
├── config/
│   ├── settings/
│   │   ├── base.py       # Settings compartidos
│   │   ├── development.py # Settings de desarrollo
│   │   └── production.py  # Settings de producción
│   └── urls.py
└── manage.py
```

## Arquitectura: Modelos + Services

### Modelos (Datos)
Los modelos Django son "tontos" y solo contienen:
- Estructura de datos
- Relaciones
- `__str__()`

### Services (Lógica de Negocio)
La lógica de validación está en `apps/asignaciones/services/`:

**ValidadorConflictos:**
- Detecta solapamiento de horarios entre cargas
- Previene que un profesor sea asignado a dos materias al mismo tiempo

**ValidadorHoras:**
- Valida que las horas de los bloques coincidan con las horas de la materia

**PeriodoService:**
- Gestiona finalización de periodos
- Obtiene estadísticas

Ver `apps/asignaciones/services/README.md` para documentación completa.

## Base de Datos

Por defecto usa **SQLite** (`db.sqlite3`).

### Cambiar a PostgreSQL (Opcional)

1. Instalar PostgreSQL
2. Crear la base de datos:
   ```sql
   CREATE DATABASE sistema_cargas_db;
   ```
3. Descomentar la configuración de PostgreSQL en `config/settings/development.py`
4. Instalar el driver:
   ```bash
   pip install psycopg2-binary
   ```
5. Actualizar `.env` con tus credenciales

## Variables de Entorno

Crea un archivo `.env` (hay un `.env.example` como referencia):

```env
SECRET_KEY=tu-secret-key-aqui
DJANGO_SETTINGS_MODULE=config.settings.development

# Solo si usas PostgreSQL
DB_NAME=sistema_cargas_db
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432
```

## Próximos Pasos

1. ✅ Modelos creados
2. ✅ Services implementados
3. ✅ Serializers implementados (ver `SERIALIZERS.md`)
4. ✅ ViewSets y Endpoints REST (ver `ENDPOINTS.md`)
5. ⏳ Testing (pendiente)
6. ⏳ Documentación de API con Swagger (pendiente)

## API REST Implementada

### Endpoints Disponibles

**Core** (`/api/core/`)
- `unidades-academicas/` - CRUD + acciones (programas, profesores)
- `programas-academicos/` - CRUD + acciones (materias, cargas)
- `usuarios/` - CRUD + acciones (me, cambiar_password)

**Académico** (`/api/academico/`)
- `profesores/` - CRUD + acciones (cargas, disponibilidad)
- `materias/` - CRUD + acciones (cargas)

**Asignaciones** (`/api/asignaciones/`)
- `periodos/` - CRUD + acciones (finalizar, estadisticas, cargas_problematicas)
- `cargas/` - CRUD + acciones (validar_disponibilidad, validar, por_estado)
- `bloques-horarios/` - Solo lectura

### Características
- ✅ Filtrado por campos relacionados
- ✅ Búsqueda de texto
- ✅ Ordenamiento
- ✅ Paginación
- ✅ Permisos por rol
- ✅ Validación automática de conflictos
- ✅ Acciones custom

Ver documentación completa en `ENDPOINTS.md`

## Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Verificar proyecto
python manage.py check

# Ejecutar tests
python manage.py test
```

## Contribución

Este proyecto está en desarrollo activo. Los modelos y services están implementados siguiendo principios de arquitectura limpia (Clean Architecture).
