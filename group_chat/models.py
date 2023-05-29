from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from notification.models import GroupNotification

class GroupChatRoom(models.Model):
    """
    A group room for people to chat in.
    """

    title = models.CharField(max_length=255, unique=False, blank=False)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        help_text="Users who belong to the group",
        related_name="group_chat_users",
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=False,
        help_text="Users with more privileges",
        related_name="admins",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=False,
        help_text="The user who created the group",
        related_name="owner",
    )

    def __str__(self):
        return self.title

    def add_user(self, user):
        """
        Returns True if user is aded to the users list
        """
        is_user_added = False
        # Check if user is not in users list
        if user not in self.users.all():
            self.users.add(user)
            self.save()
            # Create UnreadGroupChatRoomMessages object
            UnreadGroupChatRoomMessages.objects.create(room=self, user=user)
            is_user_added = True
        return is_user_added
    
    def remove_user(self, user):
        """
        Returns True if user is removed from users list
        """
        is_user_removed = False
        # Check if user is in the users list
        if user in self.users.all():
            self.users.remove(user)
            self.save()
            # Delete UnreadGroupChatRoomMessages object
            ug = UnreadGroupChatRoomMessages.objects.get(user=user, room=self)
            ug.delete()
            is_user_removed = True
        return is_user_removed
    
    def add_admin(self, user):
        """
        Add user to admins group
        """
        # Check if user is in the users list
        if user in self.users.all():
            # Add user to admins group
            self.admins.add(user)
            self.save()

    def remove_admin(self, user):
        """
        Remove user from admins group
        """
        # Check if user is admin
        if user in self.admins.all():
            self.admins.remove(user)
            self.save()
    
    def is_admin(self, user):
        """
        Returns True if given user is in the admin group
        """
        is_admin = False
        if user in self.admins.all():
            is_admin = True
        return is_admin
    
    def is_owner(self, user):
        """
        Returns True if given user is the owner of the group
        """
        is_owner = False
        if self.owner == user:
            is_owner = True
        return is_owner

    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return f"GroupChatRoom-{self.id}"


class GroupChatMessageManager(models.Manager):
    def by_room(self, room):
        """
        Return every message by specific room, order by latest message
        """
        qs = GroupChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs


class GroupChatMessage(models.Model):
    """
    Chat message created by a user inside a Room
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(GroupChatRoom, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(
        unique=False,
        blank=False,
    )

    objects = GroupChatMessageManager()

    def __str__(self):
        return self.content


class UnreadGroupChatRoomMessages(models.Model):
	"""
	Keep track of the number of unread messages by a specific user in a specific private chat.
	When the user connects the chat room, the messages will be considered "read" and 'count' will be set to 0.
	"""
	room = models.ForeignKey(GroupChatRoom, on_delete=models.CASCADE, related_name="room")

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	count = models.IntegerField(default=0)

	most_recent_message = models.CharField(max_length=500, blank=True, null=True)

	# last time msgs were read by the user
	reset_timestamp = models.DateTimeField()

	notifications = GenericRelation(GroupNotification)


	def __str__(self):
		return f"Messages that {str(self.user.username)} has not read yet."

	def save(self, *args, **kwargs):
		if not self.id: # if just created, add a timestamp. Otherwise do not automatically change it ever.
			self.reset_timestamp = timezone.now()
		return super(UnreadGroupChatRoomMessages, self).save(*args, **kwargs)

	@property
	def get_cname(self):
		"""
		For determining what kind of object is associated with a Notification
		"""
		return "UnreadGroupChatRoomMessages"

	@property
	def get_group_name(self):
		"""
		Get the group name
		"""
		return self.room.title

@receiver(pre_save, sender=UnreadGroupChatRoomMessages)
def increment_unread_msg_count(sender, instance, **kwargs):
	"""
	When the unread message count increases, update the notification. 
	If one does not exist, create one. (This should never happen)
	"""
	if instance.id is None: # new object will be created
		pass 
	else:
		previous = UnreadGroupChatRoomMessages.objects.get(id=instance.id)
		if previous.count < instance.count: # if count is incremented
			content_type = ContentType.objects.get_for_model(instance)
			try:
				notification = GroupNotification.objects.get(target=instance.user, content_type=content_type, object_id=instance.id)
				notification.verb = instance.most_recent_message
				notification.timestamp = timezone.now()
				notification.save()
			except GroupNotification.DoesNotExist:
				instance.notifications.create(
					target=instance.user,
					from_group=instance.room.title,
					redirect_url=f"{settings.BASE_URL}/group_chat/?room_id={instance.room.id}",
					verb=instance.most_recent_message,
					content_type=content_type,
				)


@receiver(pre_save, sender=UnreadGroupChatRoomMessages)
def remove_unread_msg_count_notification(sender, instance, **kwargs):
	"""
	If the unread messge count decreases, it means the user joined the chat. So delete the notification.
	"""
	if instance.id is None: # new object will be created
		pass 
	else:
		previous = UnreadGroupChatRoomMessages.objects.get(id=instance.id)
		if previous.count > instance.count: # if count is decremented
			content_type = ContentType.objects.get_for_model(instance)
			try:
				notification = GroupNotification.objects.get(target=instance.user, content_type=content_type, object_id=instance.id)
				notification.delete()
			except GroupNotification.DoesNotExist:
				pass