from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from django.urls import path

from public_chat.consumers import PublicChatConsumer
from chat.consumers import ChatConsumer
from notification.consumers import NotificationConsumer
from group_chat.consumers import GroupChatConsumer

# Define connection type (mapping type names to ASGI applications that serve them)
application = ProtocolTypeRouter({
    # Origin validator configured in settings.ALLOWED_HOSTS
    'websocket': AllowedHostsOriginValidator(
        # Build in django authentication
        AuthMiddlewareStack(
            URLRouter([
                path('public_chat/<room_id>/', PublicChatConsumer),
                path('chat/<room_id>/', ChatConsumer),
                path('group_chat/<room_id>/', GroupChatConsumer),
                path('', NotificationConsumer),
            ])
        )
    )
})