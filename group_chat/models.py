from django.db import models
from django.conf import settings


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
