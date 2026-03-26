from django.shortcuts import render, get_object_or_404
from .models import ChatRoom, Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def chat_room(request, provider_id):
    room, created = ChatRoom.objects.get_or_create(
        user=request.user,
        provider_id=provider_id
    )

    messages = Message.objects.filter(room=room)

    return render(request, 'chat/chat.html', {
        'room': room,
        'messages': messages
    })


@login_required
def send_message(request):
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        text = request.POST.get('message')

        room = ChatRoom.objects.get(id=room_id)

        msg = Message.objects.create(
            room=room,
            sender=request.user,
            message=text
        )

        return JsonResponse({
            'message': msg.message,
            'sender': msg.sender.username
        })