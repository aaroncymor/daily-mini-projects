"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/asgi/
"""

import os

from django.urls import path, re_path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# This must be imported after get_asgi_application
# see https://channels.readthedocs.io/en/stable/topics/troubleshooting.html#improperlyconfigured-exception
from sse.consumers import ServerSentEventsConsumer

application = ProtocolTypeRouter(
    {  # Routes request based on protocol (i.e http, websocket, etc)
        "http": AuthMiddlewareStack(
            URLRouter(
                [
                    path("sse/notifications", ServerSentEventsConsumer.as_asgi()),
                    re_path("", django_asgi_app),
                ]
            )  # Routes based on url
        ),
    }
)
