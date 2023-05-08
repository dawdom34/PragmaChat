from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse

from itertools import chain
import json

from .models import PrivateChatRoom, RoomChatMessage

from users.models import Account

from chat.utils import find_or_create_private_chat


DEBUG = False

def private_chat_room_view(request):
    user = request.user

    # Check if user is authenticated
    if not user.is_authenticated:
        return redirect('login')
    
    context = {}

    # Find all chat rooms this user is a part of
    rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
    rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

    # Merge the lists
    rooms = list(chain(rooms1, rooms2))

    """
    m_and_f = [{'message': 'hey', 'friend': 'Tom'}, {'message': 'hello', 'friend': 'Ben'}]
    message = most recent message
    """
    m_and_f = []
    for room in rooms:
        # Find out whitch user is the other user from authenticated user perspective
        if room.user1 == user:
            friend = room.user2
        else:
            friend = room.user1
        m_and_f.append({'message': '', 'friend': friend})

    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG
    context['m_and_f'] = m_and_f

    return render(request, 'chat/room.html', context)

def create_or_return_private_chat(request, *args, **kwargs):
    """
    Ajax call to return private chat id or create one if does not exist
    """
    user1 = request.user
    payload = {}
    if user1.is_authenticated:
        if request.method == "POST":
            user2_id = request.POST.get("user2_id")
            try:
                user2 = Account.objects.get(pk=user2_id)
                chat = find_or_create_private_chat(user1, user2)
                payload['response'] = "Successfully got the chat."
                payload['chatroom_id'] = chat.id
            except Account.DoesNotExist:
                payload['response'] = "Unable to start a chat with that user."
    else:
        payload['response'] = "You can't start a chat if you are not authenticated."
    return HttpResponse(json.dumps(payload), content_type="application/json")
