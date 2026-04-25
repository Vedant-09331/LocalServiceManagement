from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('message/', views.chatbot_message, name='chatbot_message'),
    path('suggestions/', views.chatbot_suggestions, name='chatbot_suggestions'),
]
