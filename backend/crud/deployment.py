import os
from .settings import *
from .settings import BASE_DIR
import sys

DEBUG = True

SECRET_KEY = os.environ['MY_SECRET_KEY']

ALLOWED_HOSTS = [
    os.environ['WEBSITE_HOSTNAME'],
    'gipsy-app-guarantees-dgbqgsdhhkg2a4ea.eastus2-01.azurewebsites.net'

]

CORS_ALLOWED_ORIGINS = [
    "https://icy-tree-06332be0f.1.azurestaticapps.net",  # or the port your React app runs on
]

CSRF_TRUSTED_ORIGINS = ['https://'+os.environ['WEBSITE_HOSTNAME']]

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