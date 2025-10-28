# SED - Sistema de Evaluación Docente

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.3-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Academic-yellow.svg)]()

## 📋 Descripción

El Sistema de Evaluación Docente (SED) es una plataforma web empresarial desarrollada con Django Framework que permite a las instituciones educativas gestionar de manera eficiente el proceso de evaluación del desempeño docente. El sistema garantiza evaluaciones anónimas, seguras y estructuradas, proporcionando datos analíticos para la toma de decisiones estratégicas en la mejora continua de la calidad educativa.

## 🎯 Objetivos del Proyecto

- **Transparencia**: Facilitar evaluaciones anónimas y confidenciales del desempeño docente
- **Análisis de Datos**: Generar reportes estadísticos detallados para la toma de decisiones
- **Gestión Integral**: Administrar roles, permisos y configuraciones del sistema de manera centralizada
- **Escalabilidad**: Arquitectura modular preparada para crecimiento institucional
- **Seguridad**: Implementación de mejores prácticas en autenticación y protección de datos

## 🏗️ Arquitectura del Sistema

### Módulos Principales

- **`core/`**: Núcleo del sistema, páginas principales y navegación
- **`usuarios/`**: Gestión de autenticación, registro y perfiles de usuario
- **`alumnos/`**: Módulo de estudiantes y acceso a formularios de evaluación
- **`docentes/`**: Administración de información de profesores
- **`comision/`**: Gestión de la comisión evaluadora y procesos de revisión
- **`configuracion/`**: Parámetros configurables del sistema
- **`roles/`**: Sistema de permisos y control de acceso basado en roles (RBAC)
- **`api/`**: API RESTful para integración con sistemas externos

## 🛠️ Stack Tecnológico

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.8+ | Lenguaje de programación principal |
| Django | 5.2.3 | Framework web backend |
| PostgreSQL | 12+ | Sistema de gestión de base de datos |
| asgiref | 3.8.1 | Servidor ASGI para Django |
| psycopg2-binary | 2.9.10 | Adaptador PostgreSQL para Python |
| python-decouple | 3.8 | Gestión de variables de entorno |
| sqlparse | 0.5.3 | Parser SQL para Django |

## 📦 Requisitos Previos

Antes de comenzar con la instalación, asegúrese de tener instalado:

- **Python 3.8 o superior**: [Descargar Python](https://www.python.org/downloads/)
- **PostgreSQL 12 o superior**: [Descargar PostgreSQL](https://www.postgresql.org/download/)
- **pip**: Gestor de paquetes de Python (incluido con Python)
- **Git**: Para control de versiones [Descargar Git](https://git-scm.com/)

## 🚀 Guía de Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/usuario/sed.git
cd sed
```

### Paso 2: Crear Entorno Virtual

Es una **buena práctica** utilizar un entorno virtual para aislar las dependencias del proyecto.

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Cuando el entorno virtual esté activo, verá `(venv)` al inicio de su línea de comandos.

### Paso 3: Instalar Dependencias

Instale todas las dependencias necesarias desde el archivo `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Este comando instalará automáticamente:
- Django 5.2.3
- psycopg2-binary 2.9.10 (conector PostgreSQL)
- python-decouple 3.8 (gestión de configuración)
- asgiref 3.8.1 (soporte ASGI)
- sqlparse 0.5.3 (utilidades SQL)

### Paso 4: Configurar Variables de Entorno

Cree un archivo `.env` en la raíz del proyecto para almacenar las configuraciones sensibles:

```bash
# Crear archivo .env
touch .env  # En Linux/macOS
type nul > .env  # En Windows
```

Agregue las siguientes variables al archivo `.env`:

```env
# Django Settings
SECRET_KEY=su_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=sed_database
DB_USER=postgres
DB_PASSWORD=su_contraseña_postgresql
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=su_email@gmail.com
EMAIL_HOST_PASSWORD=su_contraseña_email
```

### Paso 5: Configurar Base de Datos PostgreSQL

#### 5.1. Crear la Base de Datos

Acceda a PostgreSQL mediante terminal o pgAdmin y ejecute:

```sql
-- Crear la base de datos
CREATE DATABASE sed_database;

-- Crear usuario (opcional, si no usa el usuario postgres por defecto)
CREATE USER sed_user WITH PASSWORD 'contraseña_segura';

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE sed_database TO sed_user;
```

#### 5.2. Verificar Configuración en `settings.py`

Asegúrese de que `settings.py` esté configurado para usar las variables de entorno:

```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

### Paso 6: Ejecutar Migraciones

Aplique las migraciones para crear las tablas en la base de datos:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 7: Crear Superusuario (Administrador)

Cree una cuenta de administrador para acceder al panel de Django Admin:

```bash
python manage.py createsuperuser
```

Siga las instrucciones en pantalla para configurar el usuario, email y contraseña.

### Paso 8: Recolectar Archivos Estáticos (Producción)

Si está preparando para producción, recopile los archivos estáticos:

```bash
python manage.py collectstatic
```

### Paso 9: Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: **http://127.0.0.1:8000/**

- **Panel de administración**: http://127.0.0.1:8000/admin/
- **Página principal**: http://127.0.0.1:8000/

## 🔧 Configuración Adicional

### Archivos Estáticos

Configure la ubicación de archivos estáticos en `settings.py`:

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

### Archivos Multimedia (Uploads)

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 🧪 Testing y Calidad de Código

### Ejecutar Tests

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de un módulo específico
python manage.py test alumnos

# Ejecutar con cobertura
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Linter y Formato de Código

```bash
# Instalar herramientas de calidad
pip install flake8 black

# Verificar estilo de código
flake8 .

# Formatear código automáticamente
black .
```

## 📊 Estructura del Proyecto

```
sed/
│
├── alumnos/              # Módulo de estudiantes
├── api/                  # API REST
├── comision/             # Gestión de comisión evaluadora
├── configuracion/        # Configuraciones del sistema
├── core/                 # Núcleo de la aplicación
├── docentes/             # Módulo de profesores
├── roles/                # Sistema de permisos
├── usuarios/             # Autenticación y usuarios
├── static/               # Archivos estáticos (CSS, JS, imágenes)
├── media/                # Archivos subidos por usuarios
├── templates/            # Templates HTML
├── manage.py             # Script de gestión de Django
├── requirements.txt      # Dependencias del proyecto
├── .env                  # Variables de entorno (no en Git)
├── .gitignore           # Archivos ignorados por Git
└── README.md            # Este archivo
```

## 🔐 Seguridad

- **Variables de Entorno**: Nunca incluya `.env` en el control de versiones
- **SECRET_KEY**: Genere una clave secreta fuerte para producción
- **DEBUG**: Siempre configure `DEBUG=False` en producción
- **ALLOWED_HOSTS**: Configure correctamente los hosts permitidos
- **HTTPS**: Use HTTPS en producción con certificados SSL/TLS
- **CSRF Protection**: Django incluye protección CSRF por defecto

## 🚀 Despliegue en Producción

### Consideraciones para Producción

1. Configure `DEBUG=False` en `.env`
2. Use un servidor web como **Nginx** o **Apache**
3. Use **Gunicorn** o **uWSGI** como servidor WSGI
4. Configure **PostgreSQL** con credenciales seguras
5. Implemente **backups automáticos** de la base de datos
6. Configure **monitoreo** y **logging**
7. Use **Redis** para caché y sesiones (opcional)

### Ejemplo con Gunicorn

```bash
pip install gunicorn
gunicorn sed.wsgi:application --bind 0.0.0.0:8000
```

## 📚 Documentación Adicional

- [Documentación de Django](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)

## 👥 Equipo de Desarrollo

Este proyecto fue desarrollado por estudiantes de la **Universidad Nacional Agraria de la Selva (UNAS)** como parte del curso de **Ingeniería de Requisitos**.

## 📄 Licencia

Este proyecto es de uso **académico**. Para uso comercial o distribución, contacte con los autores.

---

## 📞 Soporte y Contacto

Para reportar problemas o solicitar nuevas funcionalidades, por favor abra un **issue** en el repositorio de GitHub.

---

**Desarrollado con ❤️ por el equipo SED - UNAS**
