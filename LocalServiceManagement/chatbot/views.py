import json
import os

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from google import genai

from services.models import Service, Category
from bookings.models import Booking
from .models import ChatbotConversation


def _get_genai_client():
    """Return a configured google-genai client."""
    api_key = os.getenv('GEMINI_API_KEY', '')
    return genai.Client(api_key=api_key)


def _build_context(user):
    """Build a system prompt with live data from the database."""

    # Fetch categories
    categories = list(Category.objects.values_list('name', flat=True))

    # Fetch top services (limit 15 for context size)
    services = list(
        Service.objects.select_related('category')
        .values('id', 'name', 'description', 'price', 'category__name', 'rating')
        .order_by('-rating')[:15]
    )

    # Fetch user bookings if authenticated
    bookings_info = ""
    if user and user.is_authenticated:
        bookings = list(
            Booking.objects.filter(user=user)
            .select_related('service')
            .values('id', 'service__name', 'status', 'payment_status', 'booking_date')
            .order_by('-created_at')[:5]
        )
        if bookings:
            bookings_info = f"\n\nUser's recent bookings:\n{json.dumps(bookings, default=str, indent=2)}"

    system_prompt = f"""You are a helpful assistant for "Local Services" — a platform where users
book home services like plumbing, electrician, cleaning, beauty, AC repair, etc.

Available service categories: {', '.join(categories) if categories else 'Various home services'}

Current top services:
{json.dumps(services, default=str, indent=2)}
{bookings_info}

You can help users with these actions:
1. **Find Services** — Search and recommend services based on what the user needs.
2. **Check Booking Status** — Tell the user about their recent bookings.
3. **General Help** — Answer questions about the platform, pricing, how to book, etc.

Guidelines:
- Be concise and friendly.
- When recommending services, include the service name, price, and rating.
- If the user asks about their bookings and they have none, tell them kindly.
- Always respond in plain text (no markdown formatting).
- Keep responses under 150 words.
"""
    return system_prompt


@csrf_exempt
@login_required
def chatbot_message(request):
    """Handle chatbot messages via AJAX POST."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        user_message = request.POST.get('message', '').strip()

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        return JsonResponse({
            'response': "I'm currently unavailable. Please ensure the GEMINI_API_KEY is configured."
        })

    try:
        client = _get_genai_client()
        system_prompt = _build_context(request.user)

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=300,
                temperature=0.7,
            ),
        )

        bot_reply = response.text.strip()

        # Save conversation
        ChatbotConversation.objects.create(
            user=request.user,
            user_message=user_message,
            bot_response=bot_reply,
        )

        return JsonResponse({'response': bot_reply})

    except Exception as e:
        return JsonResponse({
            'response': f"Sorry, I encountered an error. Please try again later."
        })


@login_required
def chatbot_suggestions(request):
    """Return quick-action suggestions for the chatbot UI."""
    suggestions = [
        {"text": "🔍 Find AC repair services", "action": "Find AC repair services near me"},
        {"text": "📋 Check my bookings", "action": "What are my recent bookings?"},
        {"text": "💰 Show cheapest services", "action": "Show me the cheapest services available"},
    ]
    return JsonResponse({'suggestions': suggestions})
