from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages

from .models import ChatRoom, Message
from bookings.models import Booking


def _has_booking_with(user, provider):
    """Check if user has any booking with the given vendor/provider."""
    return Booking.objects.filter(
        user=user,
        vendor__user=provider,
    ).exists()


@login_required
def chat_room(request, provider_id):
    from core.models import User
    provider = get_object_or_404(User, id=provider_id)

    # Determine who is the "user" and who is the "provider"
    # The logged-in user could be either side
    is_user_side = (request.user != provider)

    if is_user_side:
        # Regular user trying to chat with a vendor — check booking exists
        if not _has_booking_with(request.user, provider):
            messages.error(
                request,
                "You can only chat with a vendor after booking their service."
            )
            return redirect('services:services_list')

    room, created = ChatRoom.objects.get_or_create(
        user=request.user if is_user_side else provider,
        provider=provider if is_user_side else request.user,
    )

    chat_messages = Message.objects.filter(room=room).order_by('timestamp')

    return render(request, 'chat/chat.html', {
        'room': room,
        'messages': chat_messages,
        'other_user': provider if is_user_side else room.user,
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