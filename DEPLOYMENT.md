# Guía de Despliegue en Render.com (con SQLite)

Esta guía te llevará paso a paso para desplegar tu API de Django en Render.com con SQLite (gratis).

## ✅ Archivos Ya Preparados

Los siguientes archivos ya están configurados y listos:
- ✅ `requirements.txt` - Dependencias de Python incluyendo Gunicorn y WhiteNoise
- ✅ `runtime.txt` - Especifica Python 3.9.13
- ✅ `build.sh` - Script para construir el proyecto
- ✅ `config/settings/production.py` - Configuración de producción con SQLite
- ✅ `.env.example` - Plantilla de variables de entorno

## ⚠️ Importante: SQLite en Producción

Tu proyecto usa **SQLite** que es simple y funciona bien para:
- ✅ Proyectos académicos o demos
- ✅ Aplicaciones con pocos usuarios concurrentes
- ✅ Bajo volumen de escrituras

**Limitaciones:**
- ⚠️ Un solo usuario puede escribir a la vez
- ⚠️ Los datos se pierden si el servicio se redespliega (a menos que uses un disco persistente)
- ⚠️ No recomendado para producción con muchos usuarios

Para este proyecto académico está perfecto! 👍

## 📋 Paso 1: Preparar el Repositorio

### 1.1 Subir cambios a GitHub

```bash
cd C:\Users\Elliot Noriega\OneDrive\Escritorio\SistemaCargasClaude\SistemaCargas-api

# Asegúrate de estar en la rama main/master
git add .
git commit -m "Preparar proyecto para despliegue en Render con SQLite"
git push origin main
```

**⚠️ IMPORTANTE:** Asegúrate de que `.env` esté en `.gitignore` para no subir tus secretos.

## 📋 Paso 2: Crear Cuenta en Render

1. Ve a [https://render.com](https://render.com)
2. Haz clic en **"Get Started for Free"**
3. Regístrate con tu cuenta de GitHub (recomendado) o email
4. Verifica tu email si es necesario

## 📋 Paso 3: Crear Web Service

1. En el Dashboard de Render, haz clic en **"New +"** → **"Web Service"**

2. Conecta tu repositorio:
   - Si es la primera vez, autoriza a Render a acceder a tus repositorios de GitHub
   - Busca y selecciona tu repositorio `SistemaCargas-api`
   - Haz clic en **"Connect"**

3. Configura el servicio:
   - **Name:** `sistema-cargas-api` (o el nombre que prefieras)
   - **Region:** `Oregon (US West)` o el más cercano a ti
   - **Branch:** `main` (o `master` según tu repo)
   - **Root Directory:** (déjalo vacío)
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
   - **Plan:** **Free**

4. **NO HAGAS CLIC EN "Create Web Service" TODAVÍA**

## 📋 Paso 4: Configurar Disco Persistente (IMPORTANTE)

Para que la base de datos SQLite NO se borre cada vez que se redespliega:

1. Antes de crear el servicio, scroll hacia abajo hasta **"Advanced"**
2. Haz clic en **"Add Disk"**
3. Configura:
   - **Name:** `database`
   - **Mount Path:** `/opt/render/project/src` (ruta donde está tu proyecto)
   - **Size:** 1 GB (suficiente para la base de datos)
4. Haz clic en **"Save"**

**Esto es CRUCIAL** - sin disco persistente, perderás todos los datos cada vez que Render redespliega.

## 📋 Paso 5: Configurar Variables de Entorno

Scroll hacia abajo hasta **"Environment Variables"** y agrega:

| Key | Value | Notas |
|-----|-------|-------|
| `SECRET_KEY` | [generar abajo] | Clave secreta de Django |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` | Usar settings de producción |
| `ALLOWED_HOSTS` | `sistema-cargas-api.onrender.com` | Reemplaza con tu URL real |
| `CORS_ALLOWED_ORIGINS` | `https://tu-app.vercel.app` | Reemplaza con tu URL de Vercel |
| `SECURE_SSL_REDIRECT` | `True` | Para forzar HTTPS |

### Cómo obtener cada valor:

#### SECRET_KEY
Genera uno seguro ejecutando en tu terminal local:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copia el resultado y úsalo como valor.

#### ALLOWED_HOSTS
- Será algo como: `sistema-cargas-api.onrender.com`
- Lo verás después de crear el servicio
- Por ahora puedes dejarlo vacío, lo actualizaremos después

#### CORS_ALLOWED_ORIGINS
- La URL de tu frontend en Vercel, por ejemplo: `https://tu-app.vercel.app`
- **SIN barra diagonal al final**
- Si tienes múltiples dominios, sepáralos con coma: `https://tu-app.vercel.app,https://otro-dominio.com`

## 📋 Paso 6: Crear el Servicio

1. Revisa que todas las variables estén configuradas
2. Revisa que el **disco persistente** esté configurado
3. Haz clic en **"Create Web Service"**
4. **⏳ Espera** entre 5-10 minutos mientras Render:
   - Clona tu repositorio
   - Instala las dependencias
   - Ejecuta las migraciones
   - Recopila archivos estáticos
   - Inicia el servidor

5. Puedes ver el progreso en los **logs** (pestaña "Logs")

## 📋 Paso 7: Obtener la URL y Actualizar Variables

1. Una vez que el despliegue termine con éxito, verás la URL de tu servicio:
   - Será algo como: `https://sistema-cargas-api.onrender.com`

2. **Actualiza las variables de entorno:**
   - Ve a **"Environment"** en el panel izquierdo
   - Edita `ALLOWED_HOSTS` y pon tu URL de Render (sin https://): `sistema-cargas-api.onrender.com`
   - Guarda los cambios
   - El servicio se reiniciará automáticamente

## 📋 Paso 8: Crear Superusuario

Necesitas crear un usuario administrador para acceder a tu API:

1. En Render, ve a tu servicio → **"Shell"** (en el menú izquierdo)
2. Haz clic en **"Launch Shell"**
3. Ejecuta:
```bash
python manage.py createsuperuser
```
4. Sigue las instrucciones:
   - Username: (elige un nombre de usuario)
   - Email: (tu email)
   - Password: (una contraseña segura)
   - Confirma la contraseña

5. Ya tienes tu usuario administrador listo!

## 📋 Paso 9: Verificar la Base de Datos

Asegúrate de que la base de datos se creó correctamente:

1. En la Shell de Render, ejecuta:
```bash
ls -lh db.sqlite3
```
2. Deberías ver el archivo de la base de datos
3. Si todo está bien, verás algo como: `-rw-r--r-- 1 render render 128K Jan 10 12:34 db.sqlite3`

## 📋 Paso 10: Actualizar Frontend

Actualiza la URL de tu API en el frontend:

1. En tu proyecto de Vercel (frontend), ve a **Settings** → **Environment Variables**
2. Actualiza o agrega:
   - `VITE_API_URL` = `https://sistema-cargas-api.onrender.com/api`
   - (Reemplaza con tu URL real de Render)
3. Ve a **Deployments** → Haz clic en los 3 puntos del último deployment → **"Redeploy"**
4. El frontend se redesplegarácon la nueva URL de la API

## 📋 Paso 11: Probar la API

Prueba que todo funcione:

1. **Test básico:**
   - Abre: `https://tu-api.onrender.com/api/`
   - Deberías ver la página de Django REST Framework

2. **Test de autenticación:**
   - Abre: `https://tu-api.onrender.com/api/token/`
   - Usa POST con las credenciales del superusuario que creaste

3. **Test desde el frontend:**
   - Abre tu app en Vercel
   - Intenta hacer login
   - Deberías poder autenticarte correctamente

4. **Test del admin:**
   - Abre: `https://tu-api.onrender.com/admin/`
   - Inicia sesión con el superusuario
   - Deberías ver el panel de administración de Django

## 🔧 Troubleshooting

### Error: "Application failed to respond"
- Verifica que `ALLOWED_HOSTS` esté configurado correctamente
- Revisa los logs en Render para ver el error específico
- Ve a **Logs** y busca mensajes de error en rojo

### Error de CORS
- Verifica que `CORS_ALLOWED_ORIGINS` tenga la URL correcta de tu frontend
- Asegúrate de que no haya espacios en la variable
- Verifica que la URL NO tenga barra diagonal al final
- Ejemplo correcto: `https://mi-app.vercel.app`
- Ejemplo incorrecto: `https://mi-app.vercel.app/`

### Los datos se borran después de redesplegar
- **Verifica que configuraste el disco persistente** en el Paso 4
- Ve a **Settings** → **Disks**
- Debe aparecer un disco montado en `/opt/render/project/src`
- Si no está, agrégalo y redespliega

### Cambios en el código no se reflejan
- Haz `git push` para subir los cambios a GitHub
- Render detectará los cambios automáticamente y redesplegaráGo to **Manual Deploy** → **"Deploy latest commit"**

### La primera petición es muy lenta
- Esto es normal en el plan gratuito
- Render "duerme" el servicio después de 15 minutos de inactividad
- La primera petición tarda 30-60 segundos en "despertar"
- Las siguientes peticiones serán rápidas

## 🔄 Actualizaciones Futuras

Cada vez que hagas cambios en tu código:

1. **Commit y push a GitHub:**
```bash
git add .
git commit -m "Tu mensaje de commit"
git push origin main
```

2. **Render detecta y redespliega automáticamente:**
   - Los cambios se detectan en ~30 segundos
   - El redespliegue tarda ~5-10 minutos
   - Los logs mostrarán el progreso

3. **Las migraciones se ejecutan automáticamente:**
   - Gracias a `build.sh`, las migraciones se aplican en cada deploy
   - No necesitas hacer nada manualmente

4. **La base de datos se mantiene:**
   - Gracias al disco persistente, los datos NO se borran
   - Puedes redesplegar sin perder información

## 🎯 Crear Datos de Prueba (Opcional)

Si quieres poblar la base de datos con datos de ejemplo:

1. En la Shell de Render, ejecuta:
```bash
# Crear unidad académica
python manage.py shell
```

2. Dentro del shell de Python:
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

- [Documentación de Render](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- `ENDPOINTS.md` - Documentación de endpoints de tu API
- `CLAUDE.md` - Documentación del proyecto

## 🎉 ¡Listo!

Tu API está desplegada y lista para usar. Puedes acceder a:

- **API Base:** `https://tu-servicio.onrender.com/api/`
- **Admin Django:** `https://tu-servicio.onrender.com/admin/`
- **Token (Login):** `https://tu-servicio.onrender.com/api/token/`
- **Endpoints:** Ver `ENDPOINTS.md`

## 📝 Checklist de Verificación

Antes de considerar el despliegue completo, verifica:

- ✅ El servicio está corriendo (status "Live" en Render)
- ✅ Disco persistente configurado y montado
- ✅ Variables de entorno configuradas correctamente
- ✅ Superusuario creado
- ✅ Frontend conectado y funcionando
- ✅ Login funciona desde el frontend
- ✅ CORS configurado correctamente
- ✅ Puedes acceder al admin de Django

---

**Nota sobre el Plan Gratuito:**
- ⏸️ El servicio se "duerme" después de 15 minutos sin uso
- 🔄 Primera petición después tarda ~30-60 seg en despertar
- 💾 Con disco persistente, los datos se mantienen entre redespliegues
- ✅ 750 horas/mes gratis (suficiente para uso continuo)
- 💡 Para producción real sin sleep, considera el plan pagado ($7/mes)

**¿Necesitas ayuda?** Si encuentras problemas:
1. Revisa los logs en Render (pestaña "Logs")
2. Verifica las variables de entorno
3. Asegúrate de que el disco persistente esté configurado
4. Contacta si necesitas más ayuda! 🚀
