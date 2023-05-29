from django.contrib import admin

from django.contrib import admin

from notification.models import Notification,GroupNotification

class NotificationAdmin(admin.ModelAdmin):
    list_filter = ['content_type',]
    list_display = ['target', 'content_type', 'timestamp']
    search_fields = ['target__username',]
    readonly_fields = []

    class Meta:
        model = Notification


admin.site.register(Notification, NotificationAdmin)

class GroupNotificationAdmin(admin.ModelAdmin):
    list_filter = ['content_type']
    list_display = ['target', 'content_type', 'timestamp']
    search_fields = ['target__username']

    class Meta:
        model = Notification


admin.site.register(GroupNotification, GroupNotificationAdmin)