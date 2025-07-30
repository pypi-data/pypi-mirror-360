# kuhl_haus/magpie/web/settings.py
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APP_VERSION = os.environ.get('APP_VERSION', 'Unknown')
CONTAINER_VERSION = os.environ.get('CONTAINER_VERSION', 'Unknown')  # TODO: deprecate in favor of IMAGE_VERSION & CONTAINER_IMAGE
IMAGE_VERSION = os.environ.get('IMAGE_VERSION', 'Unknown')  # Image versions are derived from but independent of application versions
CONTAINER_IMAGE = os.environ.get('CONTAINER_IMAGE', 'Unknown')  # Includes repository information

ASGI_APPLICATION = 'kuhl_haus.magpie.web.asgi.application'
WSGI_APPLICATION = 'kuhl_haus.magpie.web.wsgi.application'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

SERVER_IP = os.environ.get("SERVER_IP", "0.0.0.0")
SERVER_PORT = os.environ.get("SERVER_PORT", 8000)

DJANGO_SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
DJANGO_SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
DJANGO_SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

MAGPIE_DOMAIN = os.environ.get("MAGPIE_DOMAIN")
DISABLE_HTTPS = os.environ.get('DISABLE_HTTPS', 'False') == 'True'
if not MAGPIE_DOMAIN:
    SESSION_COOKIE_DOMAIN = "localhost"
    CSRF_COOKIE_DOMAIN = "localhost"
    MAGPIE_DOMAIN = "localhost"
else:
    # Production Settings
    SESSION_COOKIE_DOMAIN = MAGPIE_DOMAIN
    CSRF_COOKIE_DOMAIN = MAGPIE_DOMAIN
    if not DISABLE_HTTPS:
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if DISABLE_HTTPS:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # These need to be set to Lax in order to work with http in some browsers. See reference: https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-SESSION_COOKIE_SECURE
    COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SAMESITE = "Lax"
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SAMESITE = "None"

# Set MAGPIE_ALLOWED_DOMAIN to the i.p or domain of the Magpie service on the internal network.
# Useful to set when running the service behind a reverse proxy.
MAGPIE_ALLOWED_DOMAIN = os.environ.get("MAGPIE_ALLOWED_DOMAIN", MAGPIE_DOMAIN)
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', f".{MAGPIE_ALLOWED_DOMAIN},localhost,127.0.0.1,[::1]").split(',')

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
# All Subdomains of MAGPIE_DOMAIN are trusted for CSRF
CSRF_TRUSTED_ORIGINS = [
    f"https://*.{MAGPIE_DOMAIN}",
    f"https://{MAGPIE_DOMAIN}",
    f"http://*.{MAGPIE_DOMAIN}",
    f"http://{MAGPIE_DOMAIN}",
]

# Application definition
# https://unfoldadmin.com/docs/configuration/settings/
INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    # "unfold.contrib.filters",  # optional, if special filters are needed
    # "unfold.contrib.forms",  # optional, if special form elements are needed
    # "unfold.contrib.inlines",  # optional, if special inlines are needed
    # "unfold.contrib.import_export",  # optional, if django-import-export package is used
    # "unfold.contrib.guardian",  # optional, if django-guardian package is used
    # "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'kuhl_haus.magpie.database.apps.DatabaseConfig',
    'kuhl_haus.magpie.endpoints.apps.EndpointsConfig',
    'rest_framework',
    'django_celery_results',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kuhl_haus.magpie.web.urls'

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
                'kuhl_haus.magpie.web.context_processors.version_info',
                'kuhl_haus.magpie.web.context_processors.domain_info'
            ],
        },
    },
]

# Database
db_host = os.environ.get('POSTGRES_HOST')
if db_host:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'magpie'),
            'USER': os.environ.get('POSTGRES_USER', 'magpie'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'magpie'),
            'HOST': db_host,
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 5,
            },
            # https://docs.djangoproject.com/en/5.2/ref/settings/#conn-max-age
            # Default: 0
            #
            # The development server creates a new thread for each request it handles, negating the effect of
            # persistent connections. Don’t enable them during development.
            #
            # The lifetime of a database connection, as an integer of seconds. Use 0 to close database connections at
            # the end of each request — Django’s historical behavior — and None for unlimited persistent database
            # connections.
            'CONN_MAX_AGE': 0,

            # https://docs.djangoproject.com/en/5.2/ref/settings/#conn-health-checks
            # Default: False
            #
            # If set to True, existing persistent database connections will be health checked before they are
            # reused in each request performing database access. If the health check fails, the connection will be
            # reestablished without failing the request when the connection is no longer usable but the database
            # server is ready to accept and serve new connections (e.g. after database server restart closing
            # existing connections).
            'CONN_HEALTH_CHECKS': "True",
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'django_db.sqlite3',
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get('TZ') or os.environ.get('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration Options
# https://docs.celeryq.dev/en/stable/userguide/configuration.html
#
# Broker Settings
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-settings
#
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-url
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")

# Worker Settings
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#worker
#
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#imports
# A sequence of modules to import when the worker starts.
#
# This is used to specify the task modules to import, but also to import signal handlers and additional remote control commands, etc.
#
# The modules will be imported in the original order.
CELERY_IMPORTS = []

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#include
# Exact same semantics as imports, but can be used as a means to have different import categories.
#
# The modules in this setting are imported after the modules in imports.
CELERY_INCLUDE = [
    'kuhl_haus.magpie.canary_tasks.tasks',
]

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#conf-result-backend

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#conf-database-result-backend
CELERY_RESULT_BACKEND = 'django-db'

# Beat Settings
# https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-beat_scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# https://docs.djangoproject.com/en/5.1/ref/settings/#data-upload-max-number-fields
# The maximum number of parameters that may be received via GET or POST before
# a SuspiciousOperation (TooManyFields) is raised. You can set this to None to
# disable the check. Applications that are expected to receive an unusually
# large number of form fields should tune this setting.
#
# The number of request parameters is correlated to the amount of time needed
# to process the request and populate the GET and POST dictionaries. Large
# requests could be used as a denial-of-service attack vector if left unchecked.
# Since web servers don’t typically perform deep request inspection, it’s not
# possible to perform a similar check at that level.
#
# Default: 1000
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Flower configs

FLOWER_DOMAIN = os.environ.get("FLOWER_DOMAIN", "localhost:5555")
