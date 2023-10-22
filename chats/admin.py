from django.contrib import admin
from .models import *
# Register your models here.

class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')

# Register the ChatSession model with the custom admin class
admin.site.register(ChatSession, ChatSessionAdmin)
admin.site.register(ChatHistory)
