from django.contrib import admin

from friend_messages.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
