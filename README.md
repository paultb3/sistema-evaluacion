# SED - Sistema de Evaluación Docente

El Sistema de Evaluación Docente (SED) es una plataforma web desarrollada con Django que permite a los estudiantes evaluar el desempeño de sus docentes al finalizar cada curso. El sistema promueve la mejora continua de la enseñanza y apoya a las autoridades académicas en la toma de decisiones informadas.

## 🎯 Objetivos del Proyecto

- Facilitar la evaluación anónima y segura de los docentes por parte de los estudiantes.
- Generar reportes con estadísticas de desempeño docente.
- Ofrecer un entorno amigable para la gestión de roles y configuración del sistema.

## 🧩 Módulos del Sistema

- **alumnos**: Registro de estudiantes y acceso a formularios de evaluación.
- **docentes**: Información de los profesores evaluados.
- **comision**: Gestión de la comisión encargada del proceso de evaluación.
- **configuracion**: Parámetros personalizables del sistema.
- **roles**: Asignación de permisos y tipos de usuario (estudiante, docente, administrador, comisión).
- **core**: Página principal y navegación general del sistema.
- **usuarios**: Registro, inicio de sesión y autenticación de cuentas.
- **api**: Punto de acceso para datos en formato JSON (si aplica).

## ⚙️ Tecnologías Usadas

- Python 3
- Django 5.x
- PostgreSQL
- HTML5, CSS3, JavaScript

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/usuario/sed.git
cd sed
```

### 2. Crear y activar un entorno virtual

**En Windows:**
```bash
python -m venv mi_entorno
mi_entorno\Scripts\activate
```

**En Linux/Mac:**
```bash
python3 -m venv mi_entorno
source mi_entorno/bin/activate
```

### 3. Instalar dependencias (incluye Django y PostgreSQL)

```bash
pip install django
pip install psycopg2-binary
pip install python-decouple
```

> `psycopg2-binary` es la librería que permite conectar Django con PostgreSQL.

### 4. Configurar la base de datos en `settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nombre_basedatos',
        'USER': 'usuario_postgres',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Crear la base de datos en PostgreSQL

Abre tu terminal de PostgreSQL o pgAdmin y ejecuta:

```sql
CREATE DATABASE nombre_basedatos;
```

### 6. Ejecutar migraciones y el servidor

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## 🧪 Tests y Evaluación

Se recomienda crear pruebas para asegurar el correcto funcionamiento del sistema. Django incluye herramientas integradas para ello.

## 📚 Licencia

Este proyecto es de uso académico y fue desarrollado por estudiantes de la Universidad Nacional Agraria de la Selva (UNAS) como parte del curso de Ingeniería de Requisitos.
