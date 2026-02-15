"""
ASGI config for shikshapath project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

settings_module = 'shikshapath.deployment_settings' if os.environ.get('RENDER_EXTERNAL_HOSTNAME') else os.environ.get('DJANGO_SETTINGS_MODULE', 'shikshapath.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_asgi_application()
