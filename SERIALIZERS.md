# Documentación de Serializers

Esta documentación describe todos los serializers implementados en el Sistema de Cargas Académicas.

## Principios de Diseño

### Separación Read/Write

- **Serializers de Lectura**: Incluyen datos anidados y campos calculados para mostrar información completa
- **Serializers de Escritura**: Solo IDs, validaciones y lógica de creación/actualización
- **Serializers de Lista**: Versiones simplificadas para listados

### Validaciones

- **Nivel de campo**: Validaciones simples (tipo, formato, rango)
- **Nivel de serializer**: Validaciones que involucran múltiples campos
- **Services**: Validaciones de negocio complejas (conflictos, horas, etc.)

---

## Apps.Core

### UnidadAcademicaSerializer

**Uso:** Lectura y escritura de unidades académicas

**Campos:**
- `id` - ID de la unidad
- `nombre` - Nombre de la unidad
- `total_programas` - Cantidad de programas (calculado)
- `created_at`, `updated_at` - Timestamps

**Ejemplo:**
```json
{
  "id": 1,
  "nombre": "Facultad de Ingeniería",
  "total_programas": 5,
  "created_at": "2025-01-07T10:00:00Z"
}
```

---

### ProgramaAcademicoSerializer

**Uso:** Lectura y escritura de programas académicos

**Campos:**
- `id` - ID del programa
- `unidad_academica` - ID de la unidad (write)
- `unidad_academica_nombre` - Nombre de la unidad (read)
- `nombre` - Nombre del programa
- `total_materias` - Cantidad de materias (calculado)

**Ejemplo:**
```json
{
  "id": 1,
  "unidad_academica": 1,
  "unidad_academica_nombre": "Facultad de Ingeniería",
  "nombre": "Ingeniería en Software",
  "total_materias": 45
}
```

**Versión Lista:** `ProgramaAcademicoListSerializer` (solo id y nombre)

---

### UsuarioSerializer (Lectura)

**Uso:** Mostrar información completa de un usuario

**Campos:**
- Información básica: `id`, `username`, `email`, `first_name`, `last_name`
- Rol: `rol`, `rol_display`
- Relaciones: `unidad_academica`, `programa_academico` (con nombres)
- Estado: `is_active`, `date_joined`

**Ejemplo:**
```json
{
  "id": 1,
  "username": "jperez",
  "email": "jperez@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "rol": "RESP_PROGRAMA",
  "rol_display": "Responsable de Programa",
  "programa_academico": 1,
  "programa_academico_nombre": "Ingeniería en Software"
}
```

---

### UsuarioCreateUpdateSerializer (Escritura)

**Uso:** Crear/actualizar usuarios con validación de rol

**Validaciones:**
- Responsable de Unidad DEBE tener `unidad_academica` y NO puede tener `programa_academico`
- Responsable de Programa DEBE tener `programa_academico` y NO puede tener `unidad_academica`
- Password se hashea automáticamente

**Ejemplo de creación:**
```json
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

---

## Apps.Academico

### ProfesorSerializer

**Uso:** Lectura y escritura de profesores

**Validaciones:**
- Email único por unidad académica

**Campos:**
- `id`, `nombre`, `email`
- `unidad_academica` (ID), `unidad_academica_nombre`
- `total_cargas` - Cantidad de cargas asignadas

**Ejemplo:**
```json
{
  "id": 1,
  "unidad_academica": 1,
  "unidad_academica_nombre": "Facultad de Ingeniería",
  "nombre": "Dr. Juan Pérez",
  "email": "juan.perez@universidad.edu",
  "total_cargas": 3
}
```

---

### MateriaSerializer

**Uso:** Lectura y escritura de materias

**Validaciones:**
- Clave única por programa académico
- Horas > 0

**Campos:**
- `id`, `clave`, `nombre`, `horas`
- `programa_academico` (ID), `programa_academico_nombre`
- `total_cargas` - Cantidad de secciones

**Ejemplo:**
```json
{
  "id": 1,
  "programa_academico": 1,
  "programa_academico_nombre": "Ingeniería en Software",
  "clave": "CS101",
  "nombre": "Programación I",
  "horas": 6,
  "total_cargas": 2
}
```

---

## Apps.Asignaciones

### PeriodoSerializer

**Uso:** Lectura y escritura de periodos académicos

**Campos especiales:**
- `puede_finalizar` - Boolean calculado con `PeriodoService`
- `estadisticas` - Objeto con métricas del periodo

**Validaciones:**
- Nombre único por unidad académica

**Ejemplo:**
```json
{
  "id": 1,
  "unidad_academica": 1,
  "nombre": "2025-1",
  "finalizado": false,
  "puede_finalizar": true,
  "estadisticas": {
    "total_cargas": 150,
    "cargas_por_estado": {
      "correctas": 120,
      "pendientes": 20,
    },
    "porcentaje_completado": 80.0
  }
}
```

---

### BloqueHorarioSerializer

**Uso:** Lectura de bloques horarios (dentro de una carga)

**Campos:**
- `id`, `dia`, `dia_display`
- `hora_inicio`, `hora_fin`
- `duracion_horas` - Calculado con `ValidadorHoras`

**Validaciones:**
- `hora_fin` > `hora_inicio`

**Ejemplo:**
```json
{
  "id": 1,
  "dia": "LUN",
  "dia_display": "Lunes",
  "hora_inicio": "08:00:00",
  "hora_fin": "10:00:00",
  "duracion_horas": 2.0
}
```

---

### CargaSerializer (Lectura)

**Uso:** Mostrar información completa de una carga

**Campos:**
- IDs: `programa_academico`, `materia`, `profesor`, `periodo`
- Nombres: todos los relacionados con `_nombre`
- `estado`, `estado_display`
- `bloques` - Array de BloqueHorarioSerializer
- `total_horas_bloques` - Calculado con `ValidadorHoras`

**Ejemplo:**
```json
{
  "id": 1,
  "programa_academico": 1,
  "programa_academico_nombre": "Ingeniería en Software",
  "materia": 1,
  "materia_clave": "CS101",
  "materia_nombre": "Programación I",
  "materia_horas": 6,
  "profesor": 1,
  "profesor_nombre": "Dr. Juan Pérez",
  "periodo": 1,
  "periodo_nombre": "2025-1",
  "estado": "CORRECTA",
  "estado_display": "Correcta",
  "total_horas_bloques": 6.0,
  "bloques": [
    {
      "id": 1,
      "dia": "LUN",
      "hora_inicio": "08:00:00",
      "hora_fin": "10:00:00",
      "duracion_horas": 2.0
    },
    {
      "id": 2,
      "dia": "MIE",
      "hora_inicio": "08:00:00",
      "hora_fin": "10:00:00",
      "duracion_horas": 2.0
    },
    {
      "id": 3,
      "dia": "VIE",
      "hora_inicio": "08:00:00",
      "hora_fin": "10:00:00",
      "duracion_horas": 2.0
    }
  ]
}
```

---

### CargaCreateUpdateSerializer (Escritura) ⭐

**Uso:** Crear/actualizar cargas con validación completa

**Validaciones automáticas:**
1. ✅ Periodo no finalizado
2. ✅ Horas de bloques = horas de materia (usando `ValidadorHoras`)
3. ✅ Sin conflictos de horario (usando `ValidadorConflictos`)
4. ✅ Estado se calcula automáticamente

**Flujo:**
```
1. Validar datos básicos
2. Validar horas con ValidadorHoras
3. Validar conflictos con ValidadorConflictos
4. Crear/Actualizar carga
5. Crear bloques horarios
6. Calcular y asignar estado (PENDIENTE, CORRECTA)
```

**Ejemplo de creación:**
```json
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
```

**Respuestas de error:**

```json
// Error: Horas no coinciden
{
  "detail": "Las horas de los bloques (4h) no coinciden con las horas de la materia (6h)."
}

// Error: Conflicto de horario
{
  "detail": "El profesor Dr. Juan Pérez ya tiene asignada la materia CS102 del programa Ingeniería en Computación en horarios que se solapan con: Lunes 08:00-10:00"
}

// Error: Periodo finalizado
{
  "periodo": "No se pueden crear o modificar cargas en un periodo finalizado."
}
```

---

## Uso en Views

### Ejemplo: ViewSet con múltiples serializers

```python
from rest_framework import viewsets
from apps.asignaciones.models import Carga
from apps.asignaciones.serializers import (
    CargaSerializer,
    CargaListSerializer,
    CargaCreateUpdateSerializer
)

class CargaViewSet(viewsets.ModelViewSet):
    queryset = Carga.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CargaListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CargaCreateUpdateSerializer
        return CargaSerializer
```

---

## Ventajas de esta Arquitectura

| Aspecto | Beneficio |
|---------|-----------|
| **Separación Read/Write** | Responses claras y requests simples |
| **Validaciones en Services** | Lógica reutilizable y testeable |
| **Campos calculados** | Información útil sin consultas adicionales |
| **Serializers de lista** | Responses ligeros para listados |
| **Estado automático** | Cargas siempre tienen el estado correcto |
| **Excepciones custom** | Mensajes de error claros para el frontend |

---

## Testing

Cada serializer debe tener tests para:

```python
# Ejemplo: tests/test_serializers.py
def test_carga_valida():
    # Crear carga con horas correctas y sin conflictos
    # Esperar: estado = CORRECTA

def test_carga_horas_invalidas():
    # Crear carga con horas incorrectas
    # Esperar: HorasInvalidasException

def test_carga_conflicto_horario():
    # Crear carga con profesor ocupado
    # Esperar: ConflictoHorarioException
```
