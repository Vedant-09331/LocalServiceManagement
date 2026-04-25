from django.contrib import admin
from .models import ChatbotConversation

@admin.register(ChatbotConversation)
class ChatbotConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user_message')
