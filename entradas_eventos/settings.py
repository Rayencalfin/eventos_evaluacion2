"""
==============================================================================
PROYECTO: VENTA DE ENTRADAS PARA EVENTOS Y CONCIERTOS
Estudiante: Rayen Alejandra Calfin Melivilu | Sección: AP_N4_C1 | Año: 2026
------------------------------------------------------------------------------
DESCRIPCIÓN DEL ARCHIVO:
Configuración global del proyecto Django. Soporta desarrollo local y 
despliegue en Staging/Producción (Render) con WhiteNoise, PostgreSQL y JWT.
==============================================================================
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import dj_database_url

# Directorio raíz del proyecto (donde está manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==============================================================================
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if os.getenv('DEBUG', 'False').lower() == 'true':
        SECRET_KEY = 'clave-secreta-solo-para-desarrollo-local'
    else:
        raise ValueError('La variable de entorno SECRET_KEY no está configurada para producción.')

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# ==============================================================================
# REGISTRO DE APLICACIONES (INSTALLED_APPS)
# ==============================================================================
INSTALLED_APPS = [
    # Aplicaciones nativas de Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías de terceros
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',

    # Aplicaciones locales del proyecto
    'usuarios.apps.UsuariosConfig',
    'eventos.apps.EventosConfig',
    'carrito.apps.CarritoConfig',
    'compras.apps.ComprasConfig',
    'api.apps.ApiConfig',
]

# ==============================================================================
# MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Middleware de estáticos para producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'entradas_eventos.urls'

# ==============================================================================
# CONFIGURACIÓN DE PLANTILLAS (TEMPLATES)
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'entradas_eventos.wsgi.application'

# ==============================================================================
# CONFIGURACIÓN DE BASE DE DATOS (DUAL: DATABASE_URL O POSTGRESQL LOCAL)
# ==============================================================================
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Configuración para Staging / Render (Lee la URL de conexión de la nube)
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Configuración para Desarrollo Local (PostgreSQL 18 local)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'entradas_eventos_db'),
            'USER': os.getenv('DB_USER', 'entradas_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# ==============================================================================
# MODELO DE USUARIO PERSONALIZADO
# ==============================================================================
AUTH_USER_MODEL = 'usuarios.Usuario'

# Validadores de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internacionalización y zona horaria de Chile
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# ARCHIVOS ESTÁTICOS Y MULTIMEDIA (SINTAXIS MODERNA CON STORAGES)
# ==============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# CONFIGURACIÓN DE DJANGO REST FRAMEWORK Y JWT (SIMPLE_JWT)
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',  # Permite autenticación web (cookies/login HTML)
        'rest_framework_simplejwt.authentication.JWTAuthentication', # Permite autenticación API REST con Token JWT
        'django.contrib.auth.backends.ModelBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'TOKEN_OBTAIN_SERIALIZER': 'usuarios.tokens.CustomTokenObtainPairSerializer',
}

# ==============================================================================
# CONFIGURACIÓN DE DOCUMENTACIÓN API (DRF SPECTACULAR - OPENAPI 3.0)
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'API Plataforma de Venta de Entradas - Conciertos & Eventos',
    'DESCRIPTION': (
        'Sistema API-First para comercialización de tickets de conciertos (Caso Stray Kids). '
        'Soporta autenticación JWT con roles Espectador/Organizador, carrito persistente '
        'y transacciones ACID para compra de entradas con UUID único.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_PATCH': True,
    'COMPONENT_SPLIT_REQUEST': True,
    'SERVE_PERMISSIONS': ['api.permissions.IsOrganizador'],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
}