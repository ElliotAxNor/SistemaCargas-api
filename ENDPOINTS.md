# Documentación de Endpoints REST API

Sistema de Gestión de Cargas Académicas - Endpoints disponibles

Base URL: `http://127.0.0.1:8000/api/`

---

## Autenticación (JWT)

### Obtener Token
```http
POST /api/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refrescar Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Uso del Token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## Core - Unidades Académicas

**Base:** `/api/core/unidades-academicas/`

### Listar Unidades
```http
GET /api/core/unidades-academicas/
```

### Crear Unidad
```http
POST /api/core/unidades-academicas/

{
  "nombre": "Facultad de Ingeniería"
}
```

### Obtener Detalle
```http
GET /api/core/unidades-academicas/{id}/
```

### Actualizar Unidad
```http
PUT /api/core/unidades-academicas/{id}/
PATCH /api/core/unidades-academicas/{id}/
```

### Eliminar Unidad
```http
DELETE /api/core/unidades-academicas/{id}/
```

### Acciones Custom

#### Obtener Programas de la Unidad
```http
GET /api/core/unidades-academicas/{id}/programas/
```

#### Obtener Profesores de la Unidad
```http
GET /api/core/unidades-academicas/{id}/profesores/
```

---

## Core - Programas Académicos

**Base:** `/api/core/programas-academicos/`

### Endpoints CRUD
- `GET /api/core/programas-academicos/` - Listar
- `POST /api/core/programas-academicos/` - Crear
- `GET /api/core/programas-academicos/{id}/` - Detalle
- `PUT/PATCH /api/core/programas-academicos/{id}/` - Actualizar
- `DELETE /api/core/programas-academicos/{id}/` - Eliminar

### Filtros disponibles
```http
GET /api/core/programas-academicos/?unidad_academica=1
GET /api/core/programas-academicos/?search=ingenieria
```

### Acciones Custom

#### Obtener Materias del Programa
```http
GET /api/core/programas-academicos/{id}/materias/
```

#### Obtener Cargas del Programa
```http
GET /api/core/programas-academicos/{id}/cargas/
GET /api/core/programas-academicos/{id}/cargas/?periodo=1
```

---

## Core - Usuarios

**Base:** `/api/core/usuarios/`

⚠️ **Permisos:** Solo responsables de unidad pueden gestionar usuarios

### Endpoints CRUD
- `GET /api/core/usuarios/` - Listar
- `POST /api/core/usuarios/` - Crear (solo resp. unidad)
- `GET /api/core/usuarios/{id}/` - Detalle
- `PUT/PATCH /api/core/usuarios/{id}/` - Actualizar (solo resp. unidad)
- `DELETE /api/core/usuarios/{id}/` - Eliminar (solo resp. unidad)

### Crear Usuario
```http
POST /api/core/usuarios/

{
  "username": "jperez",
  "email": "jperez@example.com",
  "password": "contraseña123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "rol": "RESP_PROGRAMA",
  "programa_academico": 1
}
```

### Acciones Custom

#### Mi Perfil
```http
GET /api/core/usuarios/me/
```

#### Cambiar Contraseña
```http
POST /api/core/usuarios/{id}/cambiar_password/

{
  "password_actual": "contraseña123",
  "password_nuevo": "nueva123"
}
```

---

## Académico - Profesores

**Base:** `/api/academico/profesores/`

### Endpoints CRUD
- `GET /api/academico/profesores/` - Listar
- `POST /api/academico/profesores/` - Crear
- `GET /api/academico/profesores/{id}/` - Detalle
- `PUT/PATCH /api/academico/profesores/{id}/` - Actualizar
- `DELETE /api/academico/profesores/{id}/` - Eliminar

### Filtros disponibles
```http
GET /api/academico/profesores/?unidad_academica=1
GET /api/academico/profesores/?search=juan
```

### Acciones Custom

#### Obtener Cargas del Profesor
```http
GET /api/academico/profesores/{id}/cargas/
GET /api/academico/profesores/{id}/cargas/?periodo=1
```

#### Verificar Disponibilidad
```http
GET /api/academico/profesores/{id}/disponibilidad/?periodo=1

Response:
{
  "profesor": {...},
  "total_cargas": 3,
  "cargas": [...]
}
```

---

## Académico - Materias

**Base:** `/api/academico/materias/`

### Endpoints CRUD
- `GET /api/academico/materias/` - Listar
- `POST /api/academico/materias/` - Crear
- `GET /api/academico/materias/{id}/` - Detalle
- `PUT/PATCH /api/academico/materias/{id}/` - Actualizar
- `DELETE /api/academico/materias/{id}/` - Eliminar

### Crear Materia
```http
POST /api/academico/materias/

{
  "programa_academico": 1,
  "clave": "CS101",
  "nombre": "Programación I",
  "horas": 6
}
```

### Filtros disponibles
```http
GET /api/academico/materias/?programa_academico=1
GET /api/academico/materias/?horas=6
GET /api/academico/materias/?search=programacion
```

### Acciones Custom

#### Obtener Cargas de la Materia
```http
GET /api/academico/materias/{id}/cargas/
GET /api/academico/materias/{id}/cargas/?periodo=1
```

---

## Asignaciones - Periodos

**Base:** `/api/asignaciones/periodos/`

### Endpoints CRUD
- `GET /api/asignaciones/periodos/` - Listar
- `POST /api/asignaciones/periodos/` - Crear
- `GET /api/asignaciones/periodos/{id}/` - Detalle
- `PUT/PATCH /api/asignaciones/periodos/{id}/` - Actualizar
- `DELETE /api/asignaciones/periodos/{id}/` - Eliminar

### Crear Periodo
```http
POST /api/asignaciones/periodos/

{
  "unidad_academica": 1,
  "nombre": "2025-1"
}
```

### Filtros disponibles
```http
GET /api/asignaciones/periodos/?unidad_academica=1
GET /api/asignaciones/periodos/?finalizado=false
```

### Acciones Custom

#### Finalizar Periodo ⭐
```http
POST /api/asignaciones/periodos/{id}/finalizar/

Response (éxito):
{
  "mensaje": "Periodo finalizado exitosamente",
  "periodo": {...}
}

Response (error):
{
  "success": false,
  "mensaje": "No se puede finalizar el periodo. Hay 30 carga(s) con problemas.",
  "cargas_problematicas": {
    "pendientes": [...]
  }
}
```

#### Obtener Estadísticas
```http
GET /api/asignaciones/periodos/{id}/estadisticas/

Response:
{
  "total_cargas": 150,
  "cargas_por_estado": {
    "correctas": 120,
    "pendientes": 20,
  },
  "porcentaje_completado": 80.0,
  "puede_finalizar": false,
  "finalizado": false
}
```

#### Obtener Cargas Problemáticas
```http
GET /api/asignaciones/periodos/{id}/cargas_problematicas/

Response:
{
  "total_pendientes": 20,
  "pendientes": [...]
}
```

---

## Asignaciones - Cargas ⭐⭐

**Base:** `/api/asignaciones/cargas/`

### Endpoints CRUD
- `GET /api/asignaciones/cargas/` - Listar
- `POST /api/asignaciones/cargas/` - Crear (con validación automática)
- `GET /api/asignaciones/cargas/{id}/` - Detalle
- `PUT/PATCH /api/asignaciones/cargas/{id}/` - Actualizar (con validación)
- `DELETE /api/asignaciones/cargas/{id}/` - Eliminar

### Crear Carga con Validación Automática
```http
POST /api/asignaciones/cargas/

{
  "programa_academico": 1,
  "materia": 1,
  "profesor": 1,
  "periodo": 1,
  "bloques": [
    {
      "dia": "LUN",
      "hora_inicio": "08:00:00",
      "hora_fin": "10:00:00"
    },
    {
      "dia": "MIE",
      "hora_inicio": "08:00:00",
      "hora_fin": "10:00:00"
    },
    {
      "dia": "VIE",
      "hora_inicio": "08:00:00",
      "hora_fin": "10:00:00"
    }
  ]
}

Response (éxito):
{
  "id": 1,
  "estado": "CORRECTA",
  ...
}

Response (error - horas):
{
  "detail": "Las horas de los bloques (4h) no coinciden con las horas de la materia (6h)."
}

Response (error - conflicto):
{
  "detail": "El profesor Dr. Juan Pérez ya tiene asignada la materia CS102 del programa Ingeniería en Computación..."
}
```

### Filtros disponibles
```http
GET /api/asignaciones/cargas/?programa_academico=1
GET /api/asignaciones/cargas/?profesor=1
GET /api/asignaciones/cargas/?periodo=1
GET /api/asignaciones/cargas/?estado=CORRECTA
GET /api/asignaciones/cargas/?search=programacion
```

### Acciones Custom

#### Validar Disponibilidad (antes de crear)
```http
POST /api/asignaciones/cargas/validar_disponibilidad/

{
  "profesor_id": 1,
  "periodo_id": 1,
  "bloques": [
    {
      "dia": "LUN",
      "hora_inicio": "08:00:00",
      "hora_fin": "10:00:00"
    }
  ]
}

Response (disponible):
{
  "disponible": true,
  "mensaje": "El profesor está disponible en los horarios especificados."
}

Response (no disponible):
{
  "disponible": false,
  "mensaje": "El profesor ya tiene asignada la materia CS102...",
  "conflicto": {
    "carga_id": 5,
    "programa": "Ingeniería en Computación",
    "materia": "Algoritmos",
    "materia_clave": "CS102"
  }
}
```

#### Validar Carga Existente
```http
GET /api/asignaciones/cargas/{id}/validar/

Response:
{
  "carga_id": 1,
  "estado_actual": "CORRECTA",
  "validaciones": {
    "horas": {
      "valida": true,
      "horas_materia": 6,
      "horas_bloques": 6.0
    },
    "conflictos": {
      "tiene_conflicto": false,
      "detalle": null
    }
  }
}
```

#### Agrupar por Estado
```http
GET /api/asignaciones/cargas/por_estado/
GET /api/asignaciones/cargas/por_estado/?periodo=1

Response:
{
  "total": 150,
  "correctas": 120,
  "pendientes": 20
}
```

---

## Asignaciones - Bloques Horarios

**Base:** `/api/asignaciones/bloques-horarios/`

⚠️ **Nota:** Solo lectura. Los bloques se gestionan a través de las cargas.

### Endpoints
- `GET /api/asignaciones/bloques-horarios/` - Listar
- `GET /api/asignaciones/bloques-horarios/{id}/` - Detalle

### Filtros disponibles
```http
GET /api/asignaciones/bloques-horarios/?carga=1
GET /api/asignaciones/bloques-horarios/?dia=LUN
```

---

## Paginación

Todos los endpoints de lista soportan paginación:

```http
GET /api/asignaciones/cargas/?page=2&page_size=50

Response:
{
  "count": 150,
  "next": "http://127.0.0.1:8000/api/asignaciones/cargas/?page=3",
  "previous": "http://127.0.0.1:8000/api/asignaciones/cargas/?page=1",
  "results": [...]
}
```

---

## Ordenamiento

Todos los endpoints de lista soportan ordenamiento:

```http
GET /api/asignaciones/cargas/?ordering=-created_at
GET /api/asignaciones/cargas/?ordering=estado,created_at
```

---

## Búsqueda

Endpoints con búsqueda de texto:

```http
GET /api/core/unidades-academicas/?search=ingenieria
GET /api/academico/profesores/?search=juan
GET /api/asignaciones/cargas/?search=programacion
```

---

## Códigos de Estado HTTP

- `200 OK` - Operación exitosa
- `201 Created` - Recurso creado
- `204 No Content` - Eliminación exitosa
- `400 Bad Request` - Datos inválidos
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - Sin permisos
- `404 Not Found` - Recurso no encontrado
- `409 Conflict` - Conflicto de horario (específico de cargas)

---

## Permisos por Rol

### Responsable de Unidad Académica
- ✅ Ver todas las cargas, programas, profesores de su unidad
- ✅ Gestionar usuarios de su unidad
- ✅ Finalizar periodos
- ✅ Todas las operaciones de lectura

### Responsable de Programa
- ✅ Ver y gestionar materias de su programa
- ✅ Ver y gestionar cargas de su programa
- ✅ Ver profesores de su unidad
- ❌ No puede gestionar usuarios
- ❌ No puede finalizar periodos
- ❌ No puede ver cargas de otros programas

---

## Testing con cURL

```bash
# Obtener token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Listar cargas (con token)
curl http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Crear carga
curl -X POST http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d @carga.json
```

---

## Próximos Pasos

1. ⏳ Documentación con Swagger/OpenAPI
2. ⏳ Tests automatizados
3. ⏳ Rate limiting
4. ⏳ Webhooks/Signals para notificaciones
