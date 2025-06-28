"""
WSGI config for pmb_hello project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Update the settings module to use the new path and project name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.core.pmb_core.settings')

application = get_wsgi_application()
