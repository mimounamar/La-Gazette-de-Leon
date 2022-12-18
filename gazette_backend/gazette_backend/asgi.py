"""
ASGI config for gazette_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gazette_backend.settings')
django.setup()
app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import gazette_backend.routing



application = ProtocolTypeRouter({
    'http': app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            gazette_backend.routing.websocket_patterns
        )
    )
})
