from django.contrib import admin
from .models import Thread, Message

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant1', 'participant2', 'created', 'updated']
    search_fields = ['participant1__username', 'participant2__username']
    list_filter = ['created', 'updated']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'text', 'thread', 'created', 'is_read']
    search_fields = ['sender__username', 'text']
    list_filter = ['created', 'is_read']
