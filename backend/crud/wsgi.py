import os
import sys

from django.core.wsgi import get_wsgi_application

settings_module = 'crud.deployment' if 'WEBSITE_HOSTNAME' in os.environ else 'crud.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

# Get the WSGI application for the project.
application = get_wsgi_application()