# Quickstart - Probar la API

Guía rápida para probar todos los endpoints del sistema.

---

## 1. Levantar el Servidor

```bash
python manage.py runserver
```

El servidor estará en: `http://127.0.0.1:8000`

---

## 2. Obtener Token JWT

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"admin123\"}"
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Guarda el access token para usarlo en los siguientes requests.**

---

## 3. Crear Datos de Prueba

### 3.1. Crear Unidad Académica

```bash
curl -X POST http://127.0.0.1:8000/api/core/unidades-academicas/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"nombre\": \"Facultad de Ingeniería\"}"
```

### 3.2. Crear Programa Académico

```bash
curl -X POST http://127.0.0.1:8000/api/core/programas-academicos/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"unidad_academica\": 1, \"nombre\": \"Ingeniería en Software\"}"
```

### 3.3. Crear Profesor

```bash
curl -X POST http://127.0.0.1:8000/api/academico/profesores/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"unidad_academica\": 1, \"nombre\": \"Dr. Juan Pérez\", \"email\": \"juan.perez@universidad.edu\"}"
```

### 3.4. Crear Materia

```bash
curl -X POST http://127.0.0.1:8000/api/academico/materias/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"programa_academico\": 1, \"clave\": \"CS101\", \"nombre\": \"Programación I\", \"horas\": 6}"
```

### 3.5. Crear Periodo

```bash
curl -X POST http://127.0.0.1:8000/api/asignaciones/periodos/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"unidad_academica\": 1, \"nombre\": \"2025-1\"}"
```

---

## 4. Crear Carga con Validación Automática ⭐

### 4.1. Crear Carga Válida

```bash
curl -X POST http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "programa_academico": 1,
    "materia": 1,
    "profesor": 1,
    "periodo": 1,
    "bloques": [
      {"dia": "LUN", "hora_inicio": "08:00:00", "hora_fin": "10:00:00"},
      {"dia": "MIE", "hora_inicio": "08:00:00", "hora_fin": "10:00:00"},
      {"dia": "VIE", "hora_inicio": "08:00:00", "hora_fin": "10:00:00"}
    ]
  }'
```

**Expected:** Estado = CORRECTA (6 horas en bloques = 6 horas de materia)

### 4.2. Validar Disponibilidad ANTES de Crear

```bash
curl -X POST http://127.0.0.1:8000/api/asignaciones/cargas/validar_disponibilidad/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profesor_id": 1,
    "periodo_id": 1,
    "bloques": [
      {"dia": "LUN", "hora_inicio": "08:00:00", "hora_fin": "10:00:00"}
    ]
  }'
```

**Expected:** `disponible: false` (porque ya tiene una carga en ese horario)

### 4.3. Intentar Crear Carga con Conflicto

```bash
curl -X POST http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "programa_academico": 1,
    "materia": 1,
    "profesor": 1,
    "periodo": 1,
    "bloques": [
      {"dia": "LUN", "hora_inicio": "08:00:00", "hora_fin": "10:00:00"}
    ]
  }'
```

**Expected:** Error 409 - Conflicto de horario

### 4.4. Intentar Crear Carga con Horas Incorrectas

```bash
curl -X POST http://127.0.0.1:8000/api/asignaciones/cargas/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "programa_academico": 1,
    "materia": 1,
    "profesor": 1,
    "periodo": 1,
    "bloques": [
      {"dia": "LUN", "hora_inicio": "08:00:00", "hora_fin": "10:00:00"}
    ]
  }'
```

**Expected:** Error 400 - Horas no coinciden (2h bloques != 6h materia)

---

## 5. Consultar Información

### 5.1. Listar Cargas del Periodo

```bash
curl http://127.0.0.1:8000/api/asignaciones/cargas/?periodo=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5.2. Ver Disponibilidad de un Profesor

```bash
curl http://127.0.0.1:8000/api/academico/profesores/1/disponibilidad/?periodo=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5.3. Ver Estadísticas del Periodo

```bash
curl http://127.0.0.1:8000/api/asignaciones/periodos/1/estadisticas/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5.4. Ver Cargas por Estado

```bash
curl http://127.0.0.1:8000/api/asignaciones/cargas/por_estado/?periodo=1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 6. Gestión de Periodo

### 6.1. Ver Cargas Problemáticas

```bash
curl http://127.0.0.1:8000/api/asignaciones/periodos/1/cargas_problematicas/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6.2. Intentar Finalizar Periodo

```bash
curl -X POST http://127.0.0.1:8000/api/asignaciones/periodos/1/finalizar/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected (si hay cargas problemáticas):**
```json
{
  "success": false,
  "mensaje": "No se puede finalizar el periodo. Hay X carga(s) con problemas.",
  "cargas_problematicas": {...}
}
```

---

## 7. Usar Filtros y Búsqueda

### 7.1. Buscar Profesores

```bash
curl "http://127.0.0.1:8000/api/academico/profesores/?search=juan" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7.2. Filtrar Cargas por Programa

```bash
curl "http://127.0.0.1:8000/api/asignaciones/cargas/?programa_academico=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7.3. Filtrar Cargas por Estado

```bash
curl "http://127.0.0.1:8000/api/asignaciones/cargas/?estado=CORRECTA" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7.4. Ordenar Cargas

```bash
curl "http://127.0.0.1:8000/api/asignaciones/cargas/?ordering=-created_at" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 8. Gestión de Usuarios

### 8.1. Ver Mi Perfil

```bash
curl http://127.0.0.1:8000/api/core/usuarios/me/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 8.2. Cambiar Mi Contraseña

```bash
curl -X POST http://127.0.0.1:8000/api/core/usuarios/1/cambiar_password/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "password_actual": "admin123",
    "password_nuevo": "nueva_contraseña123"
  }'
```

---

## 9. Testing desde el Navegador

También puedes usar la interfaz web de Django REST Framework:

1. Ve a: `http://127.0.0.1:8000/api/`
2. Navega a cualquier endpoint
3. Usa el formulario web para hacer requests

**Endpoints principales:**
- http://127.0.0.1:8000/api/core/unidades-academicas/
- http://127.0.0.1:8000/api/academico/profesores/
- http://127.0.0.1:8000/api/asignaciones/cargas/
- http://127.0.0.1:8000/api/asignaciones/periodos/

---

## 10. Herramientas Recomendadas

### Postman
- Importa la colección desde `ENDPOINTS.md`
- Crea un environment con el token

### HTTPie (alternativa a curl)

```bash
# Obtener token
http POST http://127.0.0.1:8000/api/token/ username=admin password=admin123

# Listar cargas
http http://127.0.0.1:8000/api/asignaciones/cargas/ "Authorization: Bearer YOUR_TOKEN"
```

### Insomnia
- Similar a Postman, interfaz más simple

---

## Flujo Completo de Ejemplo

```bash
# 1. Token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.access')

# 2. Crear datos base
curl -X POST http://127.0.0.1:8000/api/core/unidades-academicas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Facultad de Ingeniería"}'

# 3. Ver qué se creó
curl http://127.0.0.1:8000/api/core/unidades-academicas/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Error: 401 Unauthorized
- Verifica que el token sea correcto
- El token expira después de 1 hora (renuévalo con `/api/token/refresh/`)

### Error: 403 Forbidden
- No tienes permisos para esa operación
- Verifica que tu usuario tenga el rol correcto

### Error: 400 Bad Request
- Revisa el formato del JSON
- Verifica que todos los campos requeridos estén presentes

### Error: 409 Conflict
- Conflicto de horario detectado (es el comportamiento esperado)
- Revisa el mensaje de error para ver qué carga está en conflicto
