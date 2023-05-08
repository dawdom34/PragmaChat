from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

import json

from django.contrib.auth import get_user_model

from django.core.paginator import Paginator
from django.core.serializers.python import Serializer

from datetime import datetime

from django.db.models.base import Model

from .models import PublicChatRoom, PublicRoomChatMessage
from .constants import *

from chat.exceptions import ClientError
from chat.utils import calculate_timestamp

User = get_user_model()


# Example taken from:
# https://github.com/andrewgodwin/channels-examples/blob/master/multichat/chat/consumers.py
class PublicChatConsumer(AsyncJsonWebsocketConsumer):

	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		print("PublicChatConsumer: connect: " + str(self.scope["user"]))
		# let everyone connect. But limit read/write to authenticated users
		await self.accept()
		self.room_id = None


	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		# leave the room
		print("PublicChatConsumer: disconnect")
		try:
			if self.room_id != None:
				await self.leave_room(self.room_id)
		except:
			pass
	

	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		# Messages will have a "command" key we can switch on
		command = content.get("command", None)
		print("PublicChatConsumer: receive_json: " + str(command))
		try:
			if command == "send":
				if len(content["message"].lstrip()) == 0:
					raise ClientError(422, 'You cannot send an empty message.')
				await self.send_room(content['room_id'], content['message'])

			elif command == "join":
				# Join the room
				await self.join_room(content['room'])

			elif command == 'leave':
				# Leave the room
				await self.leave_room(content['room'])
			
			elif command == 'get_room_chat_messages':
				# Get chatroom messages from db
				# Display progress bar
				await self.display_progress_bar(True)
				# Check if room is valid
				room = await get_room_or_error(content['room_id'])
				# Get chatroom messages
				payload = await get_room_chat_messages(room, content['page_number'])
				if payload != None:
					payload = json.loads(payload)
					await self.send_messages_payload(payload['messages'], payload['new_page_number'])
				else:
					raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
				await self.display_progress_bar(False)
		except ClientError as e:
			await self.display_progress_bar(False)
			await self.handle_client_error(e)


	async def send_room(self, room_id, message):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		# Check they are in this room
		print("PublicChatConsumer: send_room")
		if self.room_id != None:
			if str(room_id) != str(self.room_id):
				raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
			if not is_authenticated(self.scope["user"]):
				raise ClientError("AUTH_ERROR", "You must be authenticated to chat.")
		else:
			raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")

		# Get the room and send to the group about it
		room = await get_room_or_error(room_id)

		# Save the message to database
		await create_public_chat_message(room, self.scope['user'], message)

		await self.channel_layer.group_send(
			room.group_name,
			{
				"type": "chat.message",
				"profile_image": self.scope["user"].profile_image.url,
				"username": self.scope["user"].username,
				"user_id": self.scope["user"].id,
				"message": message,
			}
		)

	async def chat_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		print("PublicChatConsumer: chat_message from user #" + str(event["user_id"]))
		timestamp = calculate_timestamp(datetime.now())
		await self.send_json(
			{
				"msg_type": MSG_TYPE_MESSAGE,
				"profile_image": event["profile_image"],
				"username": event["username"],
				"user_id": event["user_id"],
				"message": event["message"],
				"natural_timestamp": timestamp,
			},
		)

	async def join_room(self, room_id):
		"""
		Called by receive_json when someone sent a join command
		"""
		print("PublicChatConsumer: join_room")
		is_auth = is_authenticated(self.scope["user"])
		try:
			room = await get_room_or_error(room_id)
		except ClientError as e:
			await self.handle_client_error(e)

		# Add user to "users" list for room
		if is_auth:
			await connect_user(room, self.scope["user"])

		# Store that we're in the room
		self.room_id = room.id

		# Add them to the group so they get room messages
		await self.channel_layer.group_add(
			room.group_name,
			self.channel_name,
		)

		# Instruct their client to finish opening the room
		await self.send_json({
			"join": str(room.id)
		})

		# Send the new user count to the room
		num_connected_users = get_num_connected_users(room)
		await self.channel_layer.group_send(
			room.group_name, 
			{
				"type": "connected.user.count",
				"connected_user_count": num_connected_users,
			}
		)

	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command
		"""
		print("PublicChatConsumer: leave_room")
		is_auth = is_authenticated(self.scope["user"])
		room = await get_room_or_error(room_id)

		# Remove user from "users" list
		if is_auth:
			await disconnect_user(room, self.scope["user"])

		# Remove that we're in the room
		self.room_id = None
		# Remove them from the group so they no longer get room messages
		await self.channel_layer.group_discard(
			room.group_name,
			self.channel_name,
		)

		# Send the new user count to the room
		num_connected_users = get_num_connected_users(room)
		await self.channel_layer.group_send(
			room.group_name,
			{
				"type": "connected.user.count",
				"connected_user_count": num_connected_users,
			}
		)

	async def handle_client_error(self, e):
		"""
		Called when a ClientError is raised
		Sends error data to UI
		"""
		errorData = {}
		errorData['error'] = e.code
		if e.message:
			errorData['message'] = e.message
			await self.send_json(errorData)
		return
	
	async def send_messages_payload(self, messages, new_page_number):
		"""
		Send a payload of messages to the ui
		"""
		print('PublicChatConsumer: send_messages_payload.')

		await self.send_json({
			"messages_payload": "messages_payload",
			"messages": messages,
			"new_page_number": new_page_number,
		},)

	async def connected_user_count(self, event):
		"""
		Called to send the number of connected users to the room.
		This number is displayed in the room so other users know how many users are connected to the chat.
		"""
		# Send a message down to the client
		print("PublicChatConsumer: connected_user_count: count: " + str(event["connected_user_count"]))
		await self.send_json(
			{
				"msg_type": MSG_TYPE_CONNECTED_USER_COUNT,
				"connected_user_count": event["connected_user_count"]
			},
		)

	async def display_progress_bar(self, is_displayed):
		"""
		If is_displayed = True:
			- Display the progress bar
		If is_displayed = False:
			- Hide the progress bar
		"""
		print("DISPLAY PROGRESS BAR: " + str(is_displayed))
		await self.send_json(
			{
				"display_progress_bar": is_displayed
			}
		)

def is_authenticated(user):
	"""
	Check if user is authenticated
	"""
	if user.is_authenticated:
		return True
	return False

def get_num_connected_users(room):
	"""
	Get the number of connected users 
	"""
	if room.users:
		return len(room.users.all())
	return 0

@database_sync_to_async
def create_public_chat_message(room, user, message):
	"""
	Save the message to database
	"""
	return PublicRoomChatMessage.objects.create(user=user, room=room, content=message)

@database_sync_to_async
def connect_user(room, user):
	"""
	Add user to given room
	"""
	return room.connect_user(user)

@database_sync_to_async
def disconnect_user(room, user):
	"""
	Disconnect user from given room
	"""
	return room.disconnect_user(user)

@database_sync_to_async
def get_room_or_error(room_id):
	"""
	Check if given room exist
	"""
	try:
		room = PublicChatRoom.objects.get(id=room_id)
	except PublicChatRoom.DoesNotExist:
		raise ClientError("INVALID_ROOM", "Invalid room")
	return room

@database_sync_to_async
def get_room_chat_messages(room, page_number):
	"""
	Get paginated chat room messages
	"""
	try:
		qs = PublicRoomChatMessage.objects.by_room(room)
		p = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

		payload = {}
		messages_data = None
		new_page_number = int(page_number)
		if new_page_number <= p.num_pages:
			new_page_number += 1
			s = ChatMessageEncoder()
			payload['messages'] = s.serialize(p.page(page_number).object_list)
		else:
			payload['messages'] = 'None'
		payload['new_page_number'] = new_page_number
		return json.dumps(payload)
	except Exception as e:
		print('EXCEPTION: ' + str(e))
		return None

		
class ChatMessageEncoder(Serializer):
	def get_dump_object(self, obj: Model):
		dump_object = {}
		dump_object.update({'msg_type': MSG_TYPE_MESSAGE})
		dump_object.update({'user_id': str(obj.user.id)})
		dump_object.update({'msg_id': str(obj.id)})
		dump_object.update({'username': str(obj.user.username)})
		dump_object.update({'message': str(obj.content)})
		dump_object.update({'profile_image': str(obj.user.profile_image.url)})
		dump_object.update({'natural_timestamp': calculate_timestamp(obj.timestamp)})
		return dump_object
		