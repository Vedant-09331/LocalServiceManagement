from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db import models

from .models import ChatRoom, Message
from bookings.models import Booking


def _has_confirmed_booking_between(user1, user2):
    """Check if there is an accepted/completed booking between these two users (one user, one vendor)."""
    return Booking.objects.filter(
        status__in=['confirmed', 'completed']
    ).filter(
        (models.Q(user=user1) & models.Q(vendor__user=user2)) |
        (models.Q(user=user2) & models.Q(vendor__user=user1))
    ).exists()


@login_required
def chat_room(request, other_user_id):
    from core.models import User
    other_user = get_object_or_404(User, id=other_user_id)

    # Check if there is an authorized booking to allow chat
    if not _has_confirmed_booking_between(request.user, other_user):
        messages.error(
            request,
            "You can only chat after a booking request has been accepted."
        )
        # Redirect based on role
        if request.user.role == 'vendor':
            return redirect('vendors:vendor_dashboard')
        return redirect('core:user_dashboard')

    # Ensure consistent room creation: user side vs provider side
    # We define room.user as the 'user' role and room.provider as the 'vendor' role
    if request.user.role == 'user':
        chat_user = request.user
        chat_provider = other_user
    else:
        chat_user = other_user
        chat_provider = request.user

    room, created = ChatRoom.objects.get_or_create(
        user=chat_user,
        provider=chat_provider,
    )

    chat_messages = Message.objects.filter(room=room).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'room': room,
        'messages': chat_messages,
        'other_user': other_user,
    })


@login_required
def send_message(request):
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        text = request.POST.get('message', '').strip()

        if not text:
            return JsonResponse({'error': 'Empty message'}, status=400)

        room = get_object_or_404(ChatRoom, id=room_id)

        # Only participants can send
        if request.user != room.user and request.user != room.provider:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        msg = Message.objects.create(
            room=room,
            sender=request.user,
            message=text
        )

        return JsonResponse({
            'id': msg.id,
            'message': msg.message,
            'sender': msg.sender.email,
            'timestamp': msg.timestamp.strftime('%I:%M %p'),
            'is_self': True,
        })

    return JsonResponse({'error': 'GET not allowed'}, status=405)


@login_required
def fetch_messages(request, room_id):
    """Polling endpoint — returns new messages as JSON."""
    room = get_object_or_404(ChatRoom, id=room_id)

    if request.user != room.user and request.user != room.provider:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    last_id = request.GET.get('after', 0)
    new_msgs = Message.objects.filter(room=room, id__gt=last_id).order_by('timestamp')

    data = [{
        'id': m.id,
        'message': m.message,
        'sender': m.sender.email,
        'timestamp': m.timestamp.strftime('%I:%M %p'),
        'is_self': m.sender == request.user,
    } for m in new_msgs]

    return JsonResponse({'messages': data})