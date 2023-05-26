from django.urls import path

from .views import group_chat_room_view

app_name = 'group_chat'

urlpattterns = [
    path('', group_chat_room_view, name='group-chat-room'),
]