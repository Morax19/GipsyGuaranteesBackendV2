import os
from .settings import *
from .settings import BASE_DIR

ALLOWED_HOST = [os.environ['WEBSITE_HOSTNAME']]

CSRF_TRUSTED_ORIGINS = ['https://'+os.environ['WEBSITE_HOSTNAME']]

DEBUG = False
