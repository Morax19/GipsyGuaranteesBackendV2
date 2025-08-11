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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'), file=sys.stderr)
print("ALLOWED_HOSTS:", ALLOWED_HOSTS, file=sys.stderr)
print("WEBSITE_HOSTNAME:", os.environ.get('WEBSITE_HOSTNAME'), file=sys.stderr)