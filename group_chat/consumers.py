from channels.generic.websocket import AsyncJsonWebsocketConsumer

from channels.db import database_sync_to_async

from .models import GroupChatRoom

from chat.exceptions import ClientError

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
				pass
			elif command == "send":
				pass
			elif command == "get_room_chat_messages":
				pass
			elif command == "get_group_info":
				group = await get_group_or_error(content['room_id'], self.scope['user'])
				payload = get_group_info(group)
				print(payload)
				if payload != None:
					payload = json.loads(payload)
					print(payload)
					await self.send_group_info_payload(payload)
				else:
					raise ClientError(204, "Something went wrong retrieving the group details.")
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
			room = await get_group_or_error(room_id, self.scope["user"])
		except Exception as e:
			return
		# Instruct their client to finish opening the room
		await self.send_json({
			"join": str(room.id),
		})



	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware
		print("GroupChatConsumer: leave_room")


	async def send_room(self, room_id, message):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		print("GroupChatConsumer: send_room")

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

	async def send_messages_payload(self, messages, new_page_number):
		"""
		Send a payload of messages to the ui
		"""
		print("GroupChatConsumer: send_messages_payload. ")

	async def display_progress_bar(self, is_displayed):
		"""
		1. is_displayed = True
			- Display the progress bar on UI
		2. is_displayed = False
			- Hide the progress bar on UI
		"""
		print("DISPLAY PROGRESS BAR: " + str(is_displayed))

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