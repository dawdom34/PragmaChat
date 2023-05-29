from django.contrib import admin
from django.core.paginator import Paginator
from django.core.cache import cache
from .models import GroupChatMessage, GroupChatRoom, UnreadGroupChatRoomMessages


class GroupChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'owner']
    search_fields = ['id', 'title']

    class Meta:
        model = GroupChatRoom


admin.site.register(GroupChatRoom, GroupChatRoomAdmin)


class CachingPaginator(Paginator):
    """
    Caching chatroom messages
    Resource: http://masnun.rocks/2017/03/20/django-admin-expensive-count-all-queries/
    """
    def _get_count(self):

        if not hasattr(self, "_count"):
            self._count = None

        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)

            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class GroupChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room', 'user', 'timestamp']
    list_display = ['room', 'user', 'timestamp', 'content']
    search_fields = ['room__title', 'user__username', 'content']
    readonly_fields = ['id', 'user', 'room', 'timestamp']

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = GroupChatMessage


admin.site.register(GroupChatMessage, GroupChatMessageAdmin)

class UnreadGroupChatRoomMessagesAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'count']
    search_fields = []
    readonly_fields = ['id']

    class Meta:
        model = UnreadGroupChatRoomMessages

admin.site.register(UnreadGroupChatRoomMessages, UnreadGroupChatRoomMessagesAdmin)