from django.urls import path

from .views import (group_chat_room_view,
                    create_group_view,
                    create_group,
                    edit_group_view)

app_name = 'group_chat'

urlpatterns = [
    path('', group_chat_room_view, name='group-chat-room'),
    path('create_group_view/', create_group_view, name='create-group-view'),
    path('create_group/', create_group, name='create-group'),
    path('edit_group/<group_id>/', edit_group_view, name='edit-group'),
]