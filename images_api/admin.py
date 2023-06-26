from django.contrib import admin
from .models import Images



class ImagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    search_fields = ('user',)
    readonly_fields=('id', 'user', 'image')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.register(Images, ImagesAdmin)