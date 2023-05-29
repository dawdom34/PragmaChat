from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.utils import timezone
from django.core.paginator import Paginator

from channels.db import database_sync_to_async

from .models import GroupChatRoom, GroupChatMessage, UnreadGroupChatRoomMessages
from .constants import *

from chat.exceptions import ClientError
from chat.utils import calculate_timestamp, RoomChatMessageEncoder

from users.models import Account

import json



class GroupChatConsumer(AsyncJsonWebsocketConsumer):


	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		print("GroupChatConsumer: connect: " + str(self.scope["user"]))

		# let everyone connect. But limit read/write to authenticated users
		await self.accept()

		# the room_id will define what it means to be "connected". If it is not None, then the user is connected.
		self.room_id = None

	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		# Messages will have a "command" key we can switch on
		print("GroupChatConsumer: receive_json")
		command = content.get("command", None)
		print(command)
		try:
			if command == "join":
				await self.join_room(content["room"])
			elif command == "leave":
				await self.leave_room(content['room'])
			elif command == "send":
				if len(content['message'].lstrip()) == 0:
					raise ClientError(422, "You can't send an empty message.")
				await self.send_room(content['room'], content['message'])
			elif command == "get_room_chat_messages":
				await self.display_progress_bar(True)
				group = await get_group_or_error(content['room_id'], self.scope['user'])
				payload = await get_group_chat_messages(group, content['page_number'])
				if payload != None:
					payload = json.loads(payload)
					await self.send_messages_payload(payload['messages'], payload['new_page_number'])
				else:
					raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
				await self.display_progress_bar(False)
			elif command == "get_group_info":
				await self.display_progress_bar(True)
				group = await get_group_or_error(content['room_id'], self.scope['user'])
				payload = get_group_info(group)
				print(payload)
				if payload != None:
					payload = json.loads(payload)
					print(payload)
					await self.send_group_info_payload(payload)
				else:
					raise ClientError(204, "Something went wrong retrieving the group details.")
				await self.display_progress_bar(False)
		except ClientError as e:
			await self.handle_client_error(e)

	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		# Leave the room
		print("GroupChatConsumer: disconnect")
		pass

	async def join_room(self, room_id):
		"""
		Called by receive_json when someone sent a join command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware (AuthMiddlewareStack)
		print("GroupChatConsumer: join_room: " + str(room_id))
		try:
			group = await get_group_or_error(room_id, self.scope["user"])
		except ClientError as e:
			return await self.handle_client_error(e)
		
		# Add user to 'connected_users' list
		await connect_user(group, self.scope['user'])

		# Reset unread messages count after user connects to the room
		await on_user_connected(group, self.scope["user"])
		
		# Store that user is in the room
		self.room_id = group.id

		#  Add user to the group so he can  get room messages 
		await self.channel_layer.group_add(
			group.group_name,
			self.channel_name
		)

		# Instruct their client to finish opening the room
		await self.send_json({
			"join": str(group.id),
		})



	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware
		print("GroupChatConsumer: leave_room")

		group = await get_group_or_error(room_id, self.scope['user'])

		# Remove user from "connected_users" list
		await disconnect_user(group, self.scope["user"])

		# Remove that we're in the room
		self.room_id = None

		# Remove them from the group so they no longer get room messages
		await self.channel_layer.group_discard(
			group.group_name,
			self.channel_name,
		)
		# Instruct their client to finish closing the room
		await self.send_json({
			"leave": str(group.id),
		})


	async def send_room(self, room_id, message):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		print("GroupChatConsumer: send_room")
		# Check they are in this room
		if self.room_id != None:
			if str(room_id) != str(self.room_id):
				raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
			else:
				pass

		# Get the room and send to the group about it
		group = await get_group_or_error(room_id, self.scope["user"])

		# Create group chat message obj in database
		await create_room_chat_message(group, self.scope["user"], message)

		await self.channel_layer.group_send(
			group.group_name,
			{
				"type": "chat.message",
				"profile_image": self.scope["user"].profile_image.url,
				"username": self.scope["user"].username,
				"user_id": self.scope["user"].id,
				"message": message,
			}
		)

	# These helper methods are named by the types we send - so chat.join becomes chat_join
	async def chat_join(self, event):
		"""
		Called when someone has joined our chat.
		"""
		# Send a message down to the client
		print("GroupChatConsumer: chat_join: " + str(self.scope["user"].id))

	async def chat_leave(self, event):
		"""
		Called when someone has left our chat.
		"""
		# Send a message down to the client
		print("GroupChatConsumer: chat_leave")

	async def chat_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		print("GroupChatConsumer: chat_message")
		timestamp = calculate_timestamp(timezone.now())

		await self.send_json(
			{
				"msg_type": MSG_TYPE_MESSAGE,
				"username": event["username"],
				"user_id": event["user_id"],
				"profile_image": event["profile_image"],
				"message": event["message"],
				"natural_timestamp": timestamp,
			},
		)

	async def send_messages_payload(self, messages, new_page_number):
		"""
		Send a payload of messages to the ui
		"""
		print("GroupChatConsumer: send_messages_payload. ")
		await self.send_json(
			{
				"messages_payload": "messages_payload",
				"messages": messages,
				"new_page_number": new_page_number,
			},
		)

	async def display_progress_bar(self, is_displayed):
		"""
		1. is_displayed = True
			- Display the progress bar on UI
		2. is_displayed = False
			- Hide the progress bar on UI
		"""
		print("DISPLAY PROGRESS BAR: " + str(is_displayed))
		await self.send_json(
			{
				"display_progress_bar": is_displayed
			}
		)

	async def send_group_info_payload(self, group_info):
		"""
		Send a payload of group information to the ui
		"""
		print("GroupChatConsumer: send_group_info_payload. ")
		await self.send_json({
			"group_info": group_info,
		},)

	async def handle_client_error(self, e):
		"""
		Called when a ClientError is raised.
		Sends error data to UI
		"""
		errorData = {}
		errorData['error'] = e.code
		if e.message:
			errorData['message'] = e.message
			await self.send_json(errorData)


		

@database_sync_to_async
def get_group_or_error(room_id, user):
	"""
    Check if room exist and if user is on the users list
    Returns Group object
    """
	try:
		group = GroupChatRoom.objects.get(id=room_id)
	except GroupChatRoom.DoesNotExist:
		raise ClientError("ROOM_INVALID", "Invalid room")
	
	if user not in group.users.all():
		raise ClientError("ROOM_ACCESS_DENIED", "You do not have permissions to join this room.")
	return group

def get_group_info(group):
	"""
    Converts basic group info to json
    """
	payload = {}
	payload['group_id'] = group.id
	payload['group_title'] = group.title
	return json.dumps(payload)

@database_sync_to_async
def create_room_chat_message(room, user, message):
	"""
	Create chat message to specific room
	"""
	return GroupChatMessage.objects.create(user=user, room=room, content=message)

@database_sync_to_async
def get_group_chat_messages(room, page_number):
	"""
	Get chat messages from specific room with pagination
	"""
	try:
		qs = GroupChatMessage.objects.by_room(room)
		p = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

		payload = {}
		messages_data = None
		new_page_number = int(page_number)  
		if new_page_number <= p.num_pages:
			new_page_number = new_page_number + 1
			s = RoomChatMessageEncoder()
			payload['messages'] = s.serialize(p.page(page_number).object_list)
		else:
			payload['messages'] = "None"
		payload['new_page_number'] = new_page_number
		return json.dumps(payload)
	except Exception as e:
		print("EXCEPTION: " + str(e))
		return None
	
@database_sync_to_async
def connect_user(room, user):
	"""
	Add user to 'connected_users' list for a given room
	"""
	account = Account.objects.get(pk=user.id)
	return room.connect_user(account)

@database_sync_to_async
def disconnect_user(room, user):
	"""
	Remove user from 'connected_users' list for a given room
	"""
	# remove from connected_users list
	account = Account.objects.get(pk=user.id)
	return room.disconnect_user(account)

@database_sync_to_async
def append_unread_msg_if_not_connected(room, user, connected_users, message, from_user):
	"""
	Increment 'unread messages' if user is not connected to the group chat
	"""
	if not user in connected_users:
		try:
			unread_msgs = UnreadGroupChatRoomMessages.objects.get(room=room, user=user)
			unread_msgs.most_recent_message = f'{from_user}: {message}'
			unread_msgs.count += 1
			unread_msgs.save()
		except UnreadGroupChatRoomMessages.DoesNotExist:
			UnreadGroupChatRoomMessages(room=room, user=user, count=1).save()
			pass

	return

@database_sync_to_async
def on_user_connected(room, user):
	"""
	Reset unread message count if user connects to the group chat
	"""
	# confirm they are in the connected users list
	connected_users = room.connected_users.all()
	if user in connected_users:
		try:
			# reset count
			unread_msgs = UnreadGroupChatRoomMessages.objects.get(room=room, user=user)
			unread_msgs.count = 0
			unread_msgs.save()
		except UnreadGroupChatRoomMessages.DoesNotExist:
			UnreadGroupChatRoomMessages(room=room, user=user).save()
			pass
	return

@database_sync_to_async
def get_connected_users(room):
	"""
	Get 'connected_users' list for a given room
	"""
	connected_users = room.connected_users.all()
	return connected_users