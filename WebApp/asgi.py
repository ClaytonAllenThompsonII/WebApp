"""
ASGI config for WebApp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from inventory.routing import websocket_urlpatterns  # Adjust this import according to your app's structure

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebApp.settings')

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Django's ASGI application to handle traditional HTTP requests
    "websocket": AuthMiddlewareStack(  # Channels layer to handle WebSocket connections
        URLRouter(
            websocket_urlpatterns  # Use WebSocket URL routing from the inventory app
        )
    ),
})
