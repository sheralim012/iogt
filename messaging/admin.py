# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import ChatbotChannel, Thread, UserThread, Message, Attachment


@admin.register(ChatbotChannel)
class ChatbotChannelAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_name', 'request_url')


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_message_at', 'subject', 'uuid', 'chatbot')
    list_filter = ('last_message_at', 'chatbot')
    raw_id_fields = ('users',)


@admin.register(UserThread)
class UserThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_active', 'is_read', 'thread', 'user')
    list_filter = ('is_active', 'is_read')


class AttachmentInlineAdmin(admin.TabularInline):
    model = Message.attachments.through


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'quick_replies',
        'rapidpro_message_id',
        'sent_at',
        'text',
        'thread',
        'sender',
    )
    list_filter = ('sent_at',)
    inlines = (AttachmentInlineAdmin,)
    exclude = ('attachments', )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created',
        'modified',
        'external_link',
        'file',
    )
    list_filter = ('created', 'modified')
