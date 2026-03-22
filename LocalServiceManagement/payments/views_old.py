import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from bookings.models import Booking
from .models import Payment

def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if payment already exists
    if hasattr(booking, 'payment'):
        payment = booking.payment
    else:
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.service.price,  # Assuming service has price field
            currency='INR'
        )

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay order
    order_data = {
        'amount': int(payment.amount * 100),  # Amount in paisa
        'currency': payment.currency,
        'payment_capture': '1'  # Auto capture
    }

    order = client.order.create(data=order_data)
    payment.razorpay_order_id = order['id']
    payment.save()

    context = {
        'booking': booking,
        'payment': payment,
        'order_id': order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': int(payment.amount * 100),
    }

    return render(request, 'payments/checkout.html', context)

def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = get_object_or_404(Payment, booking=booking)

    # Verify payment
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')
    razorpay_signature = request.GET.get('razorpay_signature')

    if razorpay_payment_id and razorpay_order_id and razorpay_signature:
        # Verify signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            # Payment verified
            payment.payment_status = 'completed'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()

            # Update booking status
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()

            # Send confirmation email
            send_mail(
                "Service Booking Confirmed",
                f"Your booking for {booking.service.name} has been confirmed successfully. Payment received.",
                "admin@localservices.com",
                [booking.user.email],
            )

        except razorpay.errors.SignatureVerificationError:
            payment.payment_status = 'failed'
            payment.save()
            return redirect('payment_failed')

    return render(request, 'payments/success.html', {
        'booking': booking,
        'payment': payment
    })

def payment_failed(request):
    return render(request, 'payments/failed.html')

@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        # Webhook handling for payment events
        payload = json.loads(request.body)
        event = payload.get('event')

        if event == 'payment.captured':
            payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
            razorpay_payment_id = payment_entity.get('id')

            try:
                payment = Payment.objects.get(razorpay_payment_id=razorpay_payment_id)
                payment.payment_status = 'completed'
                payment.save()

                # Update booking
                payment.booking.payment_status = 'paid'
                payment.booking.status = 'confirmed'
                payment.booking.save()

            except Payment.DoesNotExist:
                pass

        return HttpResponse(status=200)

    return HttpResponse(status=400)     