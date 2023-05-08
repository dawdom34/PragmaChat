from django.shortcuts import render, redirect
from django.conf import settings

from itertools import chain

from .models import PrivateChatRoom, RoomChatMessage


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
