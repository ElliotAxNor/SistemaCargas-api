# 🚀 Instrucciones Específicas para ElliotAxNor

## Tu Configuración

- **Username:** ElliotAxNor
- **Dominio:** https://elliotaxnor.pythonanywhere.com
- **API URL:** https://elliotaxnor.pythonanywhere.com/api/
- **Admin URL:** https://elliotaxnor.pythonanywhere.com/admin/

---

## 🔧 Paso 1: Configurar archivo .env

En la consola Bash de PythonAnywhere:

```bash
cd ~/SistemaCargas-api
nano .env
```

Copia y pega esto (reemplaza el SECRET_KEY):

```env
SECRET_KEY=django-insecure-GENERA-UNO-NUEVO
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=True
ALLOWED_HOSTS=elliotaxnor.pythonanywhere.com,localhost
CORS_ALLOWED_ORIGINS=https://tu-app.vercel.app,http://localhost:3000
SECURE_SSL_REDIRECT=False
```

### Generar SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y reemplázalo en el archivo .env.

**Guardar:**
- Ctrl + X
- Y
- Enter

---

## 🔧 Paso 2: Configurar archivo WSGI

1. Ve a Web tab en PythonAnywhere
2. Busca la sección "Code"
3. Haz clic en el archivo WSGI (algo como `/var/www/elliotaxnor_pythonanywhere_com_wsgi.py`)
4. **BORRA TODO** el contenido
5. Copia y pega esto:

```python
import os
import sys

# Agregar el directorio del proyecto al path
path = '/home/ElliotAxNor/SistemaCargas-api'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'

# Cargar variables de entorno desde .env
from pathlib import Path
from decouple import Config, RepositoryEnv

env_path = Path('/home/ElliotAxNor/SistemaCargas-api') / '.env'
env_config = Config(RepositoryEnv(str(env_path)))

# Establecer variables de entorno
for key in ['SECRET_KEY', 'ALLOWED_HOSTS', 'CORS_ALLOWED_ORIGINS', 'SECURE_SSL_REDIRECT', 'DEBUG']:
    try:
        value = env_config(key, default=None)
        if value is not None:
            os.environ[key] = str(value)
    except Exception as e:
        pass

# Importar Django WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. Haz clic en **"Save"** (arriba a la derecha)

---

## 🔧 Paso 3: Configurar Virtualenv

En la Web tab:

1. Busca la sección **"Virtualenv"**
2. En el campo de texto, ingresa:
   ```
   /home/ElliotAxNor/.virtualenvs/sistemacargas-env
   ```
3. Haz clic en el check ✓

---

## 🔧 Paso 4: Configurar Static Files

En la Web tab, sección **"Static files"**:

1. Haz clic en "Enter URL" y "Enter path"
2. URL: `/static/`
3. Directory: `/home/ElliotAxNor/SistemaCargas-api/staticfiles`
4. Haz clic en el check ✓

---

## 🔧 Paso 5: Ejecutar Migraciones y Collectstatic

En la consola Bash:

```bash
cd ~/SistemaCargas-api
workon sistemacargas-env
python manage.py migrate
python manage.py collectstatic --no-input
```

---

## 🔧 Paso 6: Crear Superusuario

```bash
python manage.py createsuperuser
```

Ingresa:
- Username: (el que quieras)
- Email: (tu email)
- Password: (una contraseña segura)

---

## 🔧 Paso 7: Recargar la Aplicación

1. Ve a la pestaña **"Web"**
2. Haz clic en el botón verde **"Reload elliotaxnor.pythonanywhere.com"**
3. Espera 10 segundos

---

## ✅ Paso 8: Probar

Abre estas URLs en tu navegador:

1. **API Base:** https://elliotaxnor.pythonanywhere.com/api/
   - Deberías ver la página de Django REST Framework

2. **Admin:** https://elliotaxnor.pythonanywhere.com/admin/
   - Deberías poder hacer login con el superusuario

3. **Token:** https://elliotaxnor.pythonanywhere.com/api/token/
   - Debería mostrar el formulario de autenticación

---

## 🔍 Si Hay Errores

### Ver el Error Log:

En Web tab → Log files → Error log

### Ver qué dice el .env:

```bash
cd ~/SistemaCargas-api
cat .env
```

### Ver si collectstatic funcionó:

```bash
ls -la ~/SistemaCargas-api/staticfiles/
```

Deberías ver carpetas como `admin/`, `rest_framework/`, etc.

---

## 🎯 Configurar Frontend en Vercel

Una vez que la API funcione:

1. Ve a tu proyecto en Vercel
2. Settings → Environment Variables
3. Agrega o actualiza:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://elliotaxnor.pythonanywhere.com/api`
4. Deployments → Redeploy

---

## 📋 Checklist de Verificación

- [ ] Archivo `.env` configurado con SECRET_KEY correcto
- [ ] ALLOWED_HOSTS tiene `elliotaxnor.pythonanywhere.com`
- [ ] Archivo WSGI configurado con paths correctos
- [ ] Virtualenv apunta a `/home/ElliotAxNor/.virtualenvs/sistemacargas-env`
- [ ] Static files mapeado a `/home/ElliotAxNor/SistemaCargas-api/staticfiles`
- [ ] Migraciones ejecutadas sin errores
- [ ] Collectstatic ejecutado sin errores
- [ ] Superusuario creado
- [ ] Aplicación recargada (botón verde Reload)
- [ ] https://elliotaxnor.pythonanywhere.com/api/ funciona
- [ ] https://elliotaxnor.pythonanywhere.com/admin/ funciona
- [ ] Frontend en Vercel apunta a la API correcta

---

## 🆘 Comandos Útiles

### Activar virtualenv:
```bash
workon sistemacargas-env
```

### Ver logs en tiempo real:
```bash
tail -f /var/log/elliotaxnor.pythonanywhere.com.error.log
```

### Actualizar código desde GitHub:
```bash
cd ~/SistemaCargas-api
git pull origin main
workon sistemacargas-env
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
```

Luego: Web tab → Reload

### Abrir shell de Django:
```bash
cd ~/SistemaCargas-api
workon sistemacargas-env
python manage.py shell
```

---

## 🎉 URLs Finales

- **API:** https://elliotaxnor.pythonanywhere.com/api/
- **Admin:** https://elliotaxnor.pythonanywhere.com/admin/
- **Token:** https://elliotaxnor.pythonanywhere.com/api/token/
- **Docs:** https://elliotaxnor.pythonanywhere.com/api/ (ver ENDPOINTS.md)
