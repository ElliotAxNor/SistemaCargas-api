# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django REST Framework API for managing academic course load assignments (Sistema de Cargas Académicas). The system prevents scheduling conflicts when assigning professors to courses across different academic programs within a university.

**Key Domain Concepts:**
- **UnidadAcademica** (Academic Unit): Faculty or department (e.g., "Facultad de Ingeniería")
- **ProgramaAcademico** (Academic Program): Degree program within a unit (e.g., "Ingeniería en Software")
- **Profesor** (Professor): Shared resource across programs in the same unit
- **Materia** (Subject): Course with defined hours (e.g., 6 hours per week)
- **Periodo** (Academic Period): Semester or term (e.g., "2025-1")
- **Carga** (Load/Assignment): Assignment of a professor to a subject in a specific period
- **BloqueHorario** (Time Block): Specific day and time slot for a carga (e.g., Monday 8:00-10:00)

## Architecture: Fat Services, Thin Models

**Critical Design Principle:** Business logic lives in Services, NOT in models.

### Models (`apps/*/models.py`)
- Only data structure, relationships, and `__str__()`
- NO business logic methods (no `puede_finalizar()`, `validar_horas()`, etc.)
- Keep models "dumb" - they're just data containers

### Services (`apps/asignaciones/services/`)
- All business logic, validations, and calculations
- Three main services:
  - **ValidadorHoras**: Validates that block hours match subject hours
  - **ValidadorConflictos**: Detects schedule conflicts between assignments
  - **PeriodoService**: Period finalization and statistics

### Serializers (`apps/*/serializers.py`)
- Data validation and transformation
- Integrates Services for business rule enforcement
- **CargaCreateUpdateSerializer** automatically validates conflicts and hours on save
- Separate serializers for read (nested data) vs write (flat IDs) vs list (lightweight)

### ViewSets (`apps/*/views.py`)
- HTTP handling and permissions
- Custom actions with `@action` decorator
- Uses serializers for validation, services for complex operations

## Common Development Tasks

### Running the Development Server
```bash
# Activate virtual environment first
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Run server
python manage.py runserver
```

### Database Operations
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Access Django shell for testing
python manage.py shell
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.asignaciones.tests

# Run specific test file
python manage.py test apps.asignaciones.tests.test_services

# Run specific test class
python manage.py test apps.asignaciones.tests.test_services.ValidadorConflictosTestCase

# Run single test method
python manage.py test apps.asignaciones.tests.test_services.ValidadorConflictosTestCase.test_bloques_se_solapan_mismo_dia

# Verbose output
python manage.py test --verbosity=2
```

### Authentication
```bash
# Get JWT token (use admin/admin123 credentials)
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Use token in requests
curl http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Key Implementation Patterns

### 1. Automatic Carga State Calculation
When creating/updating a Carga, the state is AUTOMATICALLY calculated:
- **CORRECTA**: Has profesor AND bloques assigned
- **PENDIENTE**: Missing profesor OR bloques (incomplete)

This happens in `CargaCreateUpdateSerializer._actualizar_estado()` method.

### 2. Conflict Validation Flow
```python
# When creating a Carga via API:
# 1. CargaCreateUpdateSerializer.validate() runs
# 2. Calls ValidadorHoras.validar_horas_bloques()
# 3. Calls ValidadorConflictos.validar_disponibilidad_profesor()
# 4. Raises HorasInvalidasException or ConflictoHorarioException if invalid
# 5. On success, saves Carga and calls _actualizar_estado()
```

### 3. Custom Exception Handling
Custom exceptions in `common/exceptions.py`:
- `HorasInvalidasException`: Raised when block hours don't match subject hours
- `ConflictoHorarioException`: Raised when schedule conflict detected
- `PeriodoFinalizadoException`: Raised when trying to modify a finalized period

These are caught in serializers and converted to appropriate HTTP responses.

### 4. Permission System
- `IsResponsableUnidad`: Can manage all data in their unit
- `IsResponsablePrograma`: Can manage data only in their program
- User model has `rol` field and optional FK to UnidadAcademica or ProgramaAcademico
- ViewSets filter querysets based on user's assigned unit/program

### 5. Time String Handling in Views
When receiving time data from JSON (e.g., in `validar_disponibilidad` action):
```python
# Strings like "08:00:00" must be converted to datetime.time objects
from datetime import datetime
if isinstance(hora_inicio, str):
    hora_inicio = datetime.strptime(hora_inicio, '%H:%M:%S').time()
```

### 6. Serializing Service Responses
Services may return Django model instances. When returning from views, serialize them:
```python
# BAD - will cause JSON serialization error
return Response({'cargas': cargas_problematicas['pendientes']})

# GOOD - serialize model instances
return Response({
    'cargas': CargaListSerializer(cargas_problematicas['pendientes'], many=True).data
})
```

## Project Structure

```
SistemaCargas-api/
├── apps/
│   ├── core/              # Foundation: UnidadAcademica, ProgramaAcademico, Usuario
│   ├── academico/         # Professors and Subjects
│   └── asignaciones/      # Core domain: Periods, Cargas, Time Blocks
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── services/      # Business logic layer
│       │   ├── validador_conflictos.py
│       │   ├── validador_horas.py
│       │   └── periodo_service.py
│       └── tests/         # Comprehensive test suite
│           ├── test_services.py      # 17 tests for business logic
│           ├── test_serializers.py   # 13 tests for validation
│           └── test_views.py         # 24 tests for API endpoints
├── common/                # Shared utilities
│   ├── exceptions.py      # Custom exceptions
│   ├── pagination.py      # Custom pagination class
│   └── permissions.py     # Role-based permissions
├── config/
│   ├── settings/
│   │   ├── base.py       # Shared settings (JWT config, CORS, etc.)
│   │   ├── development.py # Dev settings (DEBUG=True, AllowAny permissions)
│   │   └── production.py  # Production settings
│   └── urls.py           # Main URL routing
├── db.sqlite3            # SQLite database (default)
├── ENDPOINTS.md          # Complete API documentation
├── SERIALIZERS.md        # Serializer documentation
├── QUICKSTART.md         # Quick testing guide
└── manage.py
```

## Adding New Features

### Adding a New Model
1. Define model in appropriate app's `models.py` (keep it simple, no business logic)
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Create serializers (separate Read/Write/List if needed)
5. Create ViewSet with appropriate permissions
6. Register in `urls.py`
7. Write tests in `tests/` directory

### Adding Business Logic
1. Create or update service in `apps/asignaciones/services/`
2. Make methods static (services are stateless)
3. Write comprehensive tests in `tests/test_services.py`
4. Integrate into serializers' `validate()` method or custom view actions
5. Document in `apps/asignaciones/services/README.md`

### Adding Custom Endpoint Action
```python
from rest_framework.decorators import action

@action(detail=True, methods=['get'])
def custom_action(self, request, pk=None):
    """
    Custom action on a specific object.
    GET /api/endpoint/{id}/custom_action/
    """
    obj = self.get_object()
    # Use services for business logic
    result = SomeService.do_something(obj)
    # Serialize if returning model instances
    return Response(result)
```

## Testing Guidelines

**IMPORTANT:** All 54 tests must pass before commits.

Test organization:
- **test_services.py**: Test business logic in isolation
- **test_serializers.py**: Test validation and serialization
- **test_views.py**: Test HTTP endpoints, authentication, permissions

When writing new tests:
- Use Django's `TestCase` class
- Create necessary fixtures in `setUp()` method
- Test both success and failure cases
- For API tests, use `APIClient` and `force_authenticate()`
- Verify response status codes and data structure

## Database Choice

**Current:** SQLite (default, recommended for development)
- Located at `db.sqlite3`
- No setup required
- Fast for development and testing

**Optional:** PostgreSQL (for production-like setup)
- Uncomment PostgreSQL config in `config/settings/development.py`
- Install `psycopg2-binary`
- Update `.env` with credentials

**Never use PostgreSQL for tests** - Django creates test database automatically with SQLite.

## Important URLs and Endpoints

**Authentication:**
- POST `/api/token/` - Get access/refresh tokens
- POST `/api/token/refresh/` - Refresh access token

**Core Management:**
- `/api/core/unidades-academicas/` - Academic units
- `/api/core/programas-academicos/` - Academic programs
- `/api/core/usuarios/` - User management

**Academic Data:**
- `/api/academico/profesores/` - Professors
- `/api/academico/materias/` - Subjects

**Assignment Management:**
- `/api/asignaciones/periodos/` - Academic periods
- `/api/asignaciones/cargas/` - Course assignments (main entity)
- `/api/asignaciones/bloques-horarios/` - Time blocks (read-only)

**Key Custom Actions:**
- POST `/api/asignaciones/cargas/validar_disponibilidad/` - Check professor availability
- GET `/api/asignaciones/cargas/{id}/validar/` - Validate existing assignment
- GET `/api/asignaciones/cargas/por_estado/?periodo=1` - Group by state
- POST `/api/asignaciones/periodos/{id}/finalizar/` - Finalize period
- GET `/api/asignaciones/periodos/{id}/estadisticas/` - Period statistics

## Common Gotchas

1. **Don't put business logic in models** - Use Services instead
2. **Always serialize model instances before returning from views** - Prevents JSON errors
3. **Convert time strings to time objects** when creating BloqueHorario instances in views
4. **Use appropriate serializer** - List for lists, Read for detail, Write for create/update
5. **Filter querysets by user role** - Implement in ViewSet's `get_queryset()`
6. **Estado field is read-only** - Automatically calculated, never manually set
7. **Period finalization checks** - Use `PeriodoService.puede_finalizar()` before allowing finalization
8. **Test with proper authentication** - Use `client.force_authenticate(user=self.user)` in tests

## Reference Documentation

- **ENDPOINTS.md**: Complete API endpoint documentation with examples
- **SERIALIZERS.md**: Serializer documentation with field descriptions
- **QUICKSTART.md**: Step-by-step guide to test the API with curl
- **apps/asignaciones/services/README.md**: Detailed service documentation

## Environment Variables

Create `.env` file (see `.env.example`):
```env
SECRET_KEY=your-secret-key-here
DJANGO_SETTINGS_MODULE=config.settings.development
```

## Default Credentials

**Admin user (pre-created via fixtures or manual creation):**
- Username: `admin`
- Password: `admin123`
- Access: http://127.0.0.1:8000/admin/
