# Scripts de Desarrollo

Scripts utilitarios para facilitar el desarrollo del Sistema de Cargas Académicas.

**⚠️ IMPORTANTE: Estos scripts son EXCLUSIVOS para entorno de desarrollo. NO ejecutar en producción.**

---

## 📋 Scripts Disponibles

### `populate_dev_data.py`

Crea datos base en la base de datos para facilitar desarrollo y testing manual.

#### ¿Qué crea?

- ✅ 1 Unidad Académica: "Facultad de Ingeniería y Ciencias"
- ✅ 3 Programas Académicos:
  - Ingeniería en Software
  - Ingeniería en Sistemas Computacionales
  - Ingeniería en Ciencias de Datos
- ✅ 4 Usuarios:
  - 1 Responsable de Unidad
  - 3 Responsables de Programa (uno por programa)
- ✅ 10 Profesores compartidos
- ✅ 18 Materias (6 por programa)
- ✅ 1 Periodo académico activo: "2025-1"

#### ¿Qué NO crea?

- ❌ Cargas (asignaciones de profesor-materia-horario)
- ❌ Bloques horarios
- ❌ Conflictos o datos problemáticos

**Esto permite que pruebes la creación de cargas manualmente a través de la API.**

---

## 🚀 Ejecución

### Prerrequisitos

1. Tener el entorno virtual activado:
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

2. Base de datos migrada:
   ```bash
   python manage.py migrate
   ```

### Ejecutar Script

```bash
# Desde la raíz del proyecto (SistemaCargas-api/)
python scripts/populate_dev_data.py
```

### Opciones

```bash
# Limpiar datos existentes antes de crear nuevos
python scripts/populate_dev_data.py --clean

# Ver ayuda
python scripts/populate_dev_data.py --help
```

---

## 📊 Datos Creados

### Credenciales de Usuarios

Todos los usuarios tienen la contraseña: `desarrollo123`

| Username | Rol | Email | Asignado a |
|----------|-----|-------|------------|
| `admin` | Superusuario | - | - |
| `resp_unidad` | RESP_UNIDAD | resp.unidad@universidad.edu | Facultad de Ingeniería |
| `resp_software` | RESP_PROGRAMA | resp.software@universidad.edu | Ing. en Software |
| `resp_sistemas` | RESP_PROGRAMA | resp.sistemas@universidad.edu | Ing. en Sistemas |
| `resp_datos` | RESP_PROGRAMA | resp.datos@universidad.edu | Ing. en Ciencias de Datos |

### Profesores

10 profesores compartidos:
- Dr. Roberto Sánchez
- Dra. Laura Fernández
- M.C. José Ramírez
- Dr. Patricia Torres
- M.C. Miguel Ángel Ruiz
- Dra. Carmen Díaz
- Dr. Fernando Castro
- M.C. Sofía Morales
- Dr. Alberto Jiménez
- Dra. Isabel Romero

### Materias por Programa

**Ingeniería en Software:**
- SW101 - Fundamentos de Programación (6h)
- SW102 - Estructuras de Datos (6h)
- SW201 - Programación Orientada a Objetos (6h)
- SW202 - Bases de Datos (6h)
- SW301 - Ingeniería de Software (4h)
- SW302 - Arquitectura de Software (4h)

**Ingeniería en Sistemas Computacionales:**
- SC101 - Introducción a la Computación (6h)
- SC102 - Matemáticas Discretas (6h)
- SC201 - Sistemas Operativos (6h)
- SC202 - Redes de Computadoras (6h)
- SC301 - Seguridad Informática (4h)
- SC302 - Administración de Sistemas (4h)

**Ingeniería en Ciencias de Datos:**
- CD101 - Introducción a Data Science (6h)
- CD102 - Estadística para Datos (6h)
- CD201 - Machine Learning I (6h)
- CD202 - Visualización de Datos (4h)
- CD301 - Deep Learning (6h)
- CD302 - Big Data Analytics (4h)

---

## 🎯 Casos de Uso

### 1. Primera vez configurando el proyecto

```bash
python manage.py migrate
python scripts/populate_dev_data.py
python manage.py runserver
```

Ahora puedes acceder a:
- API: http://127.0.0.1:8000/api/
- Admin: http://127.0.0.1:8000/admin/ (admin/admin123)

### 2. Resetear la base de datos

```bash
# Eliminar DB actual
rm db.sqlite3

# Recrear DB
python manage.py migrate

# Poblar con datos frescos
python scripts/populate_dev_data.py
```

### 3. Actualizar datos sin perder otros datos

```bash
# No usa --clean, respeta datos existentes
python scripts/populate_dev_data.py
```

### 4. Limpiar y recrear todo

```bash
python scripts/populate_dev_data.py --clean
```

---

## 🧪 Probar la API después de ejecutar el script

```bash
# 1. Obtener token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "resp_software", "password": "desarrollo123"}'

# 2. Listar materias (guarda el token)
curl http://127.0.0.1:8000/api/academico/materias/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Listar profesores
curl http://127.0.0.1:8000/api/academico/profesores/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Crear una carga (asignación)
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

---

## 📝 Notas

- El script es **idempotente**: puede ejecutarse múltiples veces sin duplicar datos (usa `get_or_create`)
- Si ejecutas sin `--clean`, respetará datos existentes
- Solo crea datos maestros, NO crea cargas ni horarios
- Útil para resetear el ambiente de desarrollo rápidamente
- El output tiene colores para mejor legibilidad (funciona en terminales compatibles con ANSI)

---

## 🔧 Personalización

Para modificar los datos que se crean, edita las listas en `populate_dev_data.py`:

- `programas_data`: Agrega/modifica programas académicos
- `profesores_data`: Agrega/modifica profesores
- `materias_por_programa`: Agrega/modifica materias por programa
- `responsables_data`: Agrega/modifica responsables de programa

---

## ⚠️ Advertencias

1. **NO ejecutar en producción** - Solo para desarrollo local
2. La opción `--clean` **elimina todos los datos** (excepto superusuarios)
3. Si tienes cargas creadas, usar `--clean` las eliminará
4. El script no crea el superusuario `admin`, debe crearse manualmente con:
   ```bash
   python manage.py createsuperuser
   ```

---

## 🐛 Troubleshooting

### Error: `django.core.exceptions.ImproperlyConfigured`
- Verifica que estés ejecutando desde la raíz del proyecto (`SistemaCargas-api/`)
- Verifica que el entorno virtual esté activado

### Error: `No such table`
- Ejecuta las migraciones primero: `python manage.py migrate`

### Error: `UNIQUE constraint failed`
- Ya existen datos con esos nombres
- Usa `--clean` para limpiar primero, o elimina manualmente los datos duplicados

---

## 📚 Ver también

- `QUICKSTART.md` - Guía de pruebas de la API
- `ENDPOINTS.md` - Documentación completa de endpoints
- `README.md` - Documentación general del proyecto
