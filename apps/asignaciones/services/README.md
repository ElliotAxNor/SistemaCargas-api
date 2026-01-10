# Services - Capa de Lógica de Negocio

Esta carpeta contiene los servicios que implementan la lógica de negocio del módulo de asignaciones.

## Principio de Diseño

Los **modelos Django** solo contienen:
- Estructura de datos (campos)
- Relaciones entre modelos
- Método `__str__()` básico
- Método `clean()` para validaciones a nivel de modelo (estándar Django)

Los **services** contienen toda la lógica de negocio:
- Validaciones complejas
- Reglas de negocio
- Cálculos
- Operaciones que involucran múltiples modelos

---

## Services Disponibles

### 1. ValidadorHoras

**Responsabilidad:** Validar que las horas de los bloques horarios coincidan con las horas de la materia.

**Métodos principales:**

```python
from apps.asignaciones.services import ValidadorHoras

# Calcular duración de un bloque
horas = ValidadorHoras.calcular_duracion_bloque(bloque)

# Calcular total de horas de una carga
total = ValidadorHoras.calcular_total_horas_bloques(carga)

# Validar que las horas coincidan
es_valido = ValidadorHoras.validar_horas_carga(carga)

# Validar antes de crear la carga
es_valido = ValidadorHoras.validar_horas_bloques(lista_bloques, horas_materia)
```

**Casos de uso:**
- Validar carga antes de cambiar estado a CORRECTA
- Validar al crear/editar bloques horarios
- Mostrar total de horas en la interfaz

---

### 2. ValidadorConflictos

**Responsabilidad:** Detectar conflictos de horarios entre cargas (mismo profesor, horarios solapados).

**Métodos principales:**

```python
from apps.asignaciones.services import ValidadorConflictos

# Verificar si dos bloques se solapan
hay_conflicto = ValidadorConflictos.bloques_se_solapan(bloque1, bloque2)

# Detectar conflicto en una carga existente
conflicto = ValidadorConflictos.detectar_conflicto_carga(carga)
if conflicto:
    print(f"Conflicto con {conflicto['programa']} - {conflicto['materia']}")

# Validar disponibilidad ANTES de crear carga
conflicto = ValidadorConflictos.validar_disponibilidad_profesor(
    profesor=profesor,
    periodo=periodo,
    bloques=lista_bloques
)
```

**Casos de uso:**
- Validar al crear una nueva carga
- Validar al editar bloques horarios de una carga existente
- Mostrar feedback al usuario sobre por qué no puede asignar un profesor
- Reportes de disponibilidad de profesores

**Formato de respuesta:**

```python
{
    'tiene_conflicto': True,
    'carga_conflictiva': <Carga object>,
    'programa': 'Ingeniería en Software',
    'materia': 'Algoritmos',
    'materia_clave': 'CS101',
    'bloques_conflictivos': [(bloque1, bloque2), ...]
}
```

---

### 3. PeriodoService

**Responsabilidad:** Gestionar la lógica de negocio de periodos académicos.

**Métodos principales:**

```python
from apps.asignaciones.services import PeriodoService

# Verificar si un periodo puede finalizar
puede = PeriodoService.puede_finalizar(periodo)

# Obtener cargas problemáticas
problemas = PeriodoService.obtener_cargas_problematicas(periodo)
# Retorna: {'pendientes': [...]}

# Finalizar periodo
resultado = PeriodoService.finalizar_periodo(periodo)
if resultado['success']:
    print(resultado['mensaje'])
else:
    print(resultado['cargas_problematicas'])

# Obtener estadísticas (para dashboard)
stats = PeriodoService.obtener_estadisticas_periodo(periodo)
# Retorna:
# {
#     'total_cargas': 150,
#     'cargas_por_estado': {'correctas': 120, 'pendientes': 30},
#     'porcentaje_completado': 80.0,
#     'puede_finalizar': False,
#     'finalizado': False
# }
```

**Casos de uso:**
- Validar antes de permitir finalización de periodo
- Dashboard del responsable de unidad
- Reportes de avance por periodo

---

## Ejemplo de Uso en Views

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.asignaciones.models import Carga
from apps.asignaciones.services import ValidadorConflictos, ValidadorHoras

class CargaViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['post'])
    def validar_disponibilidad(self, request):
        """
        Valida si un profesor está disponible antes de crear la carga.
        """
        profesor_id = request.data.get('profesor_id')
        periodo_id = request.data.get('periodo_id')
        bloques_data = request.data.get('bloques')

        # ... crear instancias de bloques temporales ...

        conflicto = ValidadorConflictos.validar_disponibilidad_profesor(
            profesor=profesor,
            periodo=periodo,
            bloques=bloques
        )

        if conflicto:
            return Response({
                'disponible': False,
                'mensaje': f"El profesor ya tiene asignada la materia {conflicto['materia']} del programa {conflicto['programa']}",
                'conflicto': conflicto
            }, status=status.HTTP_409_CONFLICT)

        return Response({'disponible': True}, status=status.HTTP_200_OK)
```

---

## Ventajas de esta Arquitectura

1. **Testeable:** Los services son funciones puras, fáciles de testear
2. **Reutilizable:** La misma lógica se puede usar desde views, serializers, signals, etc.
3. **Mantenible:** La lógica de negocio está centralizada y bien documentada
4. **Escalable:** Fácil agregar nuevos validadores sin tocar los modelos
5. **Clean Code:** Los modelos permanecen simples y enfocados en la estructura de datos
