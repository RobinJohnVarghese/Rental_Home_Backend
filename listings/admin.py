from django.contrib import admin
from .models import Listing,Notifications,ChatRoom,Message

class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_published', 'price', 'list_date', 'realtor')
    list_display_links = ('id', 'title')
    list_filter = ('realtor', )
    list_editable = ('is_published', )
    search_fields = ('title', 'description', 'address', 'city', 'state', 'zipcode', 'price')
    list_per_page = 25

admin.site.register(Listing, ListingAdmin)


class NotificationsAdmin(admin.ModelAdmin):
    list_editable = ['is_seen']
    list_display = ['id','fromuser','touser', 'intrested_post', 'is_seen', 'send_time']
    list_display_links = ('id', 'fromuser')
admin.site.register(Notifications,NotificationsAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_editable = ['is_seen', 'content']
    list_display = ['id','room', 'sender', 'is_seen', 'content','timestamp']
    list_display_links = ('id','room', 'sender', )
admin.site.register( Message,MessageAdmin)

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id','display_members']
    list_editable = [ ]
    list_display_links = ['display_members']
    
    def display_members(self, obj):
        return ', '.join([f'{member.id} -- ({member.name}) -- ({member.email})::' for member in obj.members.all()])
admin.site.register( ChatRoom,ChatRoomAdmin)

