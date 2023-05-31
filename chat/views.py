from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse

from itertools import chain
from datetime import datetime
import json
import pytz

from .models import PrivateChatRoom, RoomChatMessage

from users.models import Account

from friend.models import FriendList

from chat.utils import find_or_create_private_chat


DEBUG = False

def private_chat_room_view(request):
    user = request.user
    room_id = request.GET.get('room_id')

    # Check if user is authenticated
    if not user.is_authenticated:
        return redirect('login')
    
    context = {}
    if room_id:
        room = PrivateChatRoom.objects.get(pk=room_id)
        context["room"] = room

    context['debug'] = DEBUG
    context['debug_mode'] = settings.DEBUG
    context['m_and_f'] = get_recent_chatroom_messages(user)

    return render(request, 'chat/room.html', context)

def get_recent_chatroom_messages(user):
	"""
	sort in terms of most recent chats (users that you most recently had conversations with)
	"""
	# 1. Find all the rooms this user is a part of 
	rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
	rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

	# 2. merge the lists
	rooms = list(chain(rooms1, rooms2))

	# 3. find the newest msg in each room
	m_and_f = []
	for room in rooms:
		# Figure out which user is the "other user" (aka friend)
		if room.user1 == user:
			friend = room.user2
		else:
			friend = room.user1

		# confirm you are even friends (in case chat is left active somehow)
		friend_list = FriendList.objects.get(user=user)
		if not friend_list.is_mutual_friend(friend):
			chat = find_or_create_private_chat(user, friend)
			chat.is_active = False
			chat.save()
		else:	
			# find newest msg from that friend in the chat room
			try:
				message = RoomChatMessage.objects.filter(room=room, user=friend).latest("timestamp")
			except RoomChatMessage.DoesNotExist:
				# create a dummy message with dummy timestamp
				today = datetime(
					year=1950, 
					month=1, 
					day=1, 
					hour=1,
					minute=1,
					second=1,
					tzinfo=pytz.UTC
				)
				message = RoomChatMessage(
					user=friend,
					room=room,
					timestamp=today,
					content="",
				)
			m_and_f.append({
				'message': message,
				'friend': friend
			})

	return sorted(m_and_f, key=lambda x: x['message'].timestamp, reverse=True)

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
