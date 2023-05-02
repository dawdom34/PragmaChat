from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from django.urls import path

from public_chat.consumers import PublicChatConsumer

# Define connection type (mapping type names to ASGI applications that serve them)
application = ProtocolTypeRouter({
    # Origin validator configured in settings.ALLOWED_HOSTS
    'websocket': AllowedHostsOriginValidator(
        # Build in django authentication
        AuthMiddlewareStack(
            URLRouter([
                path('public_chat/<room_id>/', PublicChatConsumer)
            ])
        )
    )
})