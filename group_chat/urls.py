from django.urls import path

from .views import (group_chat_room_view,
                    create_group_view,
                    create_group,
                    edit_group_view,
                    edit_group_title,
                    add_friend_to_group,
                    remove_friend_from_group,
                    promote_to_admin)

app_name = 'group_chat'

urlpatterns = [
    path('', group_chat_room_view, name='group-chat-room'),
    path('create_group_view/', create_group_view, name='create-group-view'),
    path('create_group/', create_group, name='create-group'),
    path('edit_group/<group_id>/', edit_group_view, name='edit-group'),
    path('edit_group_title/', edit_group_title, name='edit-group-title'),
    path('add_friend_to_group/', add_friend_to_group, name='add-friend-to-group'),
    path('remove_friend_from_group/', remove_friend_from_group, name='remove-friend-from-group'),
    path('promote_to_admin', promote_to_admin, name='promote-to-admin'),
]