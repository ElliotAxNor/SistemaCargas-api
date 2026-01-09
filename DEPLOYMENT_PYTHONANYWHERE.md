# Guía de Despliegue en PythonAnywhere (con SQLite)

Esta guía te llevará paso a paso para desplegar tu API de Django en PythonAnywhere con SQLite (100% gratis).

## ✅ Por Qué PythonAnywhere

- ✅ **SQLite funciona perfectamente** - Los datos NO se pierden (persistencia incluida)
- ✅ Completamente gratis para siempre
- ✅ Diseñado específicamente para Django
- ✅ Más fácil de configurar que otras plataformas
- ✅ Perfecto para proyectos académicos
- ✅ Incluye consola Bash y editor de archivos

## ⚠️ Limitaciones del Plan Gratuito

- La aplicación "duerme" después de 3 meses de inactividad (solo necesitas hacer clic para reactivarla)
- Dominio será: `tu-usuario.pythonanywhere.com`
- CPU limitada (suficiente para proyectos académicos)
- Solo HTTPS desde sitios en lista blanca (pero puedes agregarlo desde el dashboard)

## 📋 Paso 1: Crear Cuenta en PythonAnywhere

1. Ve a [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Haz clic en **"Pricing & signup"**
3. Selecciona el plan **"Beginner"** (Free - $0/month)
4. Regístrate con tu email
5. Verifica tu email
6. Inicia sesión

## 📋 Paso 2: Subir tu Código a GitHub

Asegúrate de que tu código esté en GitHub (PythonAnywhere clonará desde ahí):

```bash
cd C:\Users\Elliot Noriega\OneDrive\Escritorio\SistemaCargasClaude\SistemaCargas-api

# Verificar que todo esté commiteado
git status

# Si hay cambios pendientes
git add .
git commit -m "Preparar proyecto para PythonAnywhere"
git push origin main
```

**⚠️ IMPORTANTE:** Verifica que `.env` esté en `.gitignore` para no subir secretos.

## 📋 Paso 3: Clonar Repositorio en PythonAnywhere

1. En el dashboard de PythonAnywhere, ve a **"Consoles"**
2. Haz clic en **"Bash"** para abrir una nueva consola
3. Clona tu repositorio:

```bash
# Clonar tu repositorio
git clone https://github.com/TU-USUARIO/SistemaCargas-api.git

# Entrar al directorio
cd SistemaCargas-api

# Verificar que todo esté bien
ls -la
```

## 📋 Paso 4: Crear Entorno Virtual e Instalar Dependencias

En la misma consola Bash:

```bash
# Crear entorno virtual con Python 3.9
mkvirtualenv --python=/usr/bin/python3.9 sistemacargas-env

# El virtualenv se activará automáticamente
# Verás (sistemacargas-env) al inicio de la línea

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

## 📋 Paso 5: Configurar Variables de Entorno

### 5.1 Generar SECRET_KEY

En la consola Bash, ejecuta:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado (será algo como: `django-insecure-abc123xyz...`)

### 5.2 Crear archivo .env

En la consola Bash:

```bash
# Crear archivo .env
nano .env
```

Pega el siguiente contenido (reemplaza los valores):

```env
# Django Settings
SECRET_KEY=TU-SECRET-KEY-GENERADO-ARRIBA
DJANGO_SETTINGS_MODULE=config.settings.production

# Hosts permitidos (reemplaza tu-usuario con tu username de PythonAnywhere)
ALLOWED_HOSTS=tu-usuario.pythonanywhere.com,localhost

# CORS - URL de tu frontend en Vercel
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app,http://localhost:3000

# Security
SECURE_SSL_REDIRECT=False
```

**Importante:** Reemplaza:
- `TU-SECRET-KEY-GENERADO-ARRIBA` con el SECRET_KEY que generaste
- `tu-usuario` con tu username de PythonAnywhere
- `https://tu-app.vercel.app` con la URL real de tu frontend

Guarda el archivo:
- Presiona `Ctrl + X`
- Presiona `Y` (Yes)
- Presiona `Enter`

## 📋 Paso 6: Ejecutar Migraciones y Recolectar Estáticos

```bash
# Asegúrate de estar en el directorio del proyecto
cd ~/SistemaCargas-api

# Activar virtualenv si no está activo
workon sistemacargas-env

# Ejecutar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Crear superusuario
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador:
- Username: (elige uno)
- Email: (tu email)
- Password: (una contraseña segura)

## 📋 Paso 7: Configurar Web App en PythonAnywhere

### 7.1 Crear Web App

1. En el dashboard, ve a la pestaña **"Web"**
2. Haz clic en **"Add a new web app"**
3. Haz clic en **"Next"** (aceptar el dominio gratuito)
4. Selecciona **"Manual configuration"** (NO uses Django wizard)
5. Selecciona **"Python 3.9"**
6. Haz clic en **"Next"**

### 7.2 Configurar Virtual Environment

En la página de configuración de Web:

1. Busca la sección **"Virtualenv"**
2. En el campo de texto, ingresa la ruta completa de tu virtualenv:
   ```
   /home/TU-USUARIO/.virtualenvs/sistemacargas-env
   ```
   (Reemplaza `TU-USUARIO` con tu username de PythonAnywhere)
3. Haz clic en el check ✓

### 7.3 Configurar WSGI

1. En la sección **"Code"**, haz clic en el enlace del archivo WSGI
   (será algo como: `/var/www/tusuario_pythonanywhere_com_wsgi.py`)

2. **Borra TODO el contenido** del archivo

3. Pega el siguiente código:

```python
import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/TU-USUARIO/SistemaCargas-api'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

# Cargar variables de entorno desde .env
from pathlib import Path
from decouple import Config, RepositoryEnv

env_path = Path('/home/TU-USUARIO/SistemaCargas-api') / '.env'
env_config = Config(RepositoryEnv(str(env_path)))

# Establecer variables de entorno
for key in ['SECRET_KEY', 'ALLOWED_HOSTS', 'CORS_ALLOWED_ORIGINS', 'SECURE_SSL_REDIRECT']:
    if env_config(key, default=None):
        os.environ[key] = env_config(key)

# Importar Django WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**⚠️ IMPORTANTE:** Reemplaza `TU-USUARIO` con tu username de PythonAnywhere en las líneas 6 y 14.

4. Haz clic en **"Save"** (arriba a la derecha)

### 7.4 Configurar Archivos Estáticos

1. Regresa a la pestaña **"Web"**
2. Scroll hacia abajo hasta la sección **"Static files"**
3. Agrega dos mapeos:

**Mapeo 1 - Static:**
- URL: `/static/`
- Directory: `/home/TU-USUARIO/SistemaCargas-api/staticfiles`

**Mapeo 2 - Media (opcional, para archivos subidos):**
- URL: `/media/`
- Directory: `/home/TU-USUARIO/SistemaCargas-api/media`

(Reemplaza `TU-USUARIO` con tu username)

### 7.5 Configurar CORS en Whitelist

Para que tu frontend en Vercel pueda conectarse:

1. Scroll hasta la sección **"Security"** o **"HTTPS"**
2. Busca **"Force HTTPS"** y verifica que esté habilitado
3. En el dashboard principal, ve a **"Account"**
4. En **"API Token"**, genera un token si aún no tienes uno
5. Regresa a **"Web"** → **"Security"**
6. Asegúrate de que tu dominio de Vercel esté permitido

## 📋 Paso 8: Recargar la Aplicación

1. En la pestaña **"Web"**, scroll hasta arriba
2. Haz clic en el botón verde **"Reload tusuario.pythonanywhere.com"**
3. Espera unos segundos

## 📋 Paso 9: Verificar que Todo Funcione

### 9.1 Test Básico

Abre en tu navegador:
```
https://tu-usuario.pythonanywhere.com/api/
```

Deberías ver la página de Django REST Framework.

### 9.2 Test del Admin

Abre:
```
https://tu-usuario.pythonanywhere.com/admin/
```

Inicia sesión con el superusuario que creaste.

### 9.3 Test de Token

Puedes probar el endpoint de autenticación:
```
https://tu-usuario.pythonanywhere.com/api/token/
```

### 9.4 Verificar Base de Datos

En la consola Bash:
```bash
cd ~/SistemaCargas-api
workon sistemacargas-env
ls -lh db.sqlite3
```

Deberías ver tu archivo de base de datos.

## 📋 Paso 10: Configurar Frontend en Vercel

1. Ve a tu proyecto de frontend en Vercel
2. Ve a **Settings** → **Environment Variables**
3. Actualiza o agrega:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://tu-usuario.pythonanywhere.com/api`
4. Ve a **Deployments**
5. Haz clic en los 3 puntos del último deployment → **"Redeploy"**

## 📋 Paso 11: Probar Conexión Frontend-Backend

1. Abre tu app de Vercel en el navegador
2. Intenta hacer login
3. Si hay errores de CORS, revisa:
   - El archivo `.env` tiene la URL correcta de Vercel
   - La variable `CORS_ALLOWED_ORIGINS` está configurada sin espacios
   - No hay barra diagonal al final de la URL

## 🔧 Troubleshooting

### Error 500 - Internal Server Error

1. Ve a **"Web"** → **"Log files"**
2. Haz clic en **"Error log"**
3. Busca el error específico en rojo
4. Causas comunes:
   - Variables de entorno mal configuradas
   - Path del virtualenv incorrecto
   - Path del proyecto incorrecto en WSGI

### Error de CORS

1. Verifica que el archivo `.env` tenga la URL correcta de Vercel
2. Verifica que NO haya espacios en `CORS_ALLOWED_ORIGINS`
3. Verifica que NO haya barra diagonal al final
4. Ejemplo correcto: `https://mi-app.vercel.app`
5. Ejemplo incorrecto: `https://mi-app.vercel.app/`

### Cambios no se reflejan

1. Ve a la consola Bash
2. Ejecuta:
   ```bash
   cd ~/SistemaCargas-api
   git pull origin main
   workon sistemacargas-env
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --no-input
   ```
3. Ve a **"Web"** → **"Reload"** (botón verde)

### Archivos estáticos no cargan

1. Verifica que ejecutaste `collectstatic`
2. Verifica la configuración de Static files en Web tab
3. El path debe ser absoluto: `/home/TU-USUARIO/SistemaCargas-api/staticfiles`

### La base de datos está vacía después de un cambio

¡Esto NO debería pasar! A diferencia de Render, PythonAnywhere mantiene tu SQLite persistente.

Si pasa:
1. Verifica que no borraste `db.sqlite3` accidentalmente
2. Puedes restaurar desde backup si lo tienes
3. O volver a crear datos de prueba

## 🔄 Actualizaciones Futuras

Cada vez que hagas cambios en tu código:

### 1. Subir a GitHub
```bash
# En tu computadora local
git add .
git commit -m "Tu mensaje"
git push origin main
```

### 2. Actualizar en PythonAnywhere

Abre consola Bash en PythonAnywhere:
```bash
cd ~/SistemaCargas-api
git pull origin main
workon sistemacargas-env
pip install -r requirements.txt  # Solo si cambiaron dependencias
python manage.py migrate  # Solo si hay nuevas migraciones
python manage.py collectstatic --no-input  # Solo si cambiaron archivos estáticos
```

### 3. Recargar la App

Ve a **"Web"** → **"Reload"** (botón verde)

## 📊 Crear Datos de Prueba (Opcional)

Si quieres poblar la base de datos con datos de ejemplo:

```bash
cd ~/SistemaCargas-api
workon sistemacargas-env
python manage.py shell
```

Dentro del shell de Python:
```python
from apps.core.models import UnidadAcademica, ProgramaAcademico
from apps.academico.models import Profesor, Materia
from apps.asignaciones.models import Periodo

# Crear unidad
unidad = UnidadAcademica.objects.create(nombre="Facultad de Ingeniería")

# Crear programa
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
exit()
```

## 📚 Recursos Útiles

- **Dashboard PythonAnywhere:** https://www.pythonanywhere.com/user/TU-USUARIO/
- **Documentación PythonAnywhere:** https://help.pythonanywhere.com/
- **Django en PythonAnywhere:** https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/
- **ENDPOINTS.md** - Documentación de endpoints de tu API
- **CLAUDE.md** - Documentación del proyecto

## 🎉 ¡Listo!

Tu API está desplegada y lista para usar en PythonAnywhere. Puedes acceder a:

- **API Base:** `https://tu-usuario.pythonanywhere.com/api/`
- **Admin Django:** `https://tu-usuario.pythonanywhere.com/admin/`
- **Token (Login):** `https://tu-usuario.pythonanywhere.com/api/token/`
- **Endpoints:** Ver `ENDPOINTS.md`

## 📝 Checklist de Verificación

- ✅ Código subido a GitHub
- ✅ Repositorio clonado en PythonAnywhere
- ✅ Virtualenv creado y dependencias instaladas
- ✅ Archivo `.env` configurado con SECRET_KEY y CORS
- ✅ Migraciones ejecutadas
- ✅ Archivos estáticos recolectados
- ✅ Superusuario creado
- ✅ Web app configurada con WSGI correcto
- ✅ Archivos estáticos mapeados
- ✅ Aplicación recargada (botón verde Reload)
- ✅ API responde en `https://tu-usuario.pythonanywhere.com/api/`
- ✅ Puedes hacer login en `/admin/`
- ✅ Frontend en Vercel conectado y funcionando
- ✅ CORS configurado correctamente

## 💡 Ventajas de PythonAnywhere vs Render

- ✅ SQLite funciona perfectamente (datos persistentes) sin pagar
- ✅ Más sencillo de configurar
- ✅ Consola Bash incluida para debugging
- ✅ Editor de archivos integrado
- ✅ No necesitas crear base de datos separada
- ✅ Perfecto para proyectos académicos

---

**¿Necesitas ayuda?** Si encuentras problemas:
1. Revisa los Error logs en Web → Log files → Error log
2. Verifica las variables de entorno en `.env`
3. Asegúrate de que los paths en WSGI sean correctos
4. Verifica que el virtualenv esté activado
5. Contacta si necesitas más ayuda! 🚀
