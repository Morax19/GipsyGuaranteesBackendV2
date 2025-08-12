import os
from .settings import *
from .settings import BASE_DIR
import sys

DEBUG = False

SECRET_KEY = os.environ.get('MY_SECRET_KEY')

ALLOWED_HOSTS = [
    os.environ.get('WEBSITE_HOSTNAME'),
    os.environ.get('CUSTOM_HOSTNAME')
]

CORS_ALLOWED_ORIGINS = [
    # URL del frontend REACT
    "https://icy-tree-06332be0f.1.azurestaticapps.net",
]

# Conexión a la BD Azure
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_SERVER'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}   

CSRF_TRUSTED_ORIGINS = [
    'https://'+os.environ.get('WEBSITE_HOSTNAME', ''),
    'https://'+os.environ.get('CUSTOM_HOSTNAME', '')
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')