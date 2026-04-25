from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:other_user_id>/', views.chat_room, name='chat_room'),
    path('send/', views.send_message, name='send_message'),
    path('fetch/<int:room_id>/', views.fetch_messages, name='fetch_messages'),
]