import os
from .settings import *
from .settings import BASE_DIR

DEBUG = False

SECRET_KEY = os.environ['MY_SECRET_KEY']

ALLOWED_HOSTS = [os.environ['WEBSITE_HOSTNAME']]

CORS_ALLOWED_ORIGINS = [
    "https://icy-tree-06332be0f.1.azurestaticapps.net/",  # or the port your React app runs on
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

#CONNECTION = os.environ['DB_CONNECTION_HERE']
#CONNECTION_STR = {pair.split('=')[0]: pair.split('=')[1] for pair in CONNECTION.split(';') if '=' in pair}
#CONNECTION_STR = {pair.split('=')[0]: pair.split('=')[1] for pair in CONNECTION.split(' ')}
DATABASES =  {
    "default": {
        "ENGINE": "django.db.backends.sqlserver",
        "NAME": CONNECTION_STR['dbname'],
        "HOST": CONNECTION_STR['host'],
        "USER": CONNECTION_STR['user'],
        "PASSWORD": CONNECTION_STR['password'],
    }
}

STATIC_ROOT = BASE_DIR/'staticfiles'