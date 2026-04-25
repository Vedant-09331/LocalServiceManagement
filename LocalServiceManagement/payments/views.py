import razorpay
import json
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from bookings.models import Booking
from .models import Payment


def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Get or create payment record
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            "amount": booking.service.price,
            "currency": "INR"
        }
    )

    try:
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay order
        order_data = {
            'amount': int(payment.amount * 100),  # Amount in paisa
            'currency': 'INR',
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

    except Exception as e:
        print(f"Razorpay Order Error: {e}")
        # Fallback to demo mode if keys are missing/invalid to prevent 500
        return render(request, 'payments/checkout.html', {
            'booking': booking,
            'payment': payment,
            'error': "Razorpay configuration missing or invalid. Using Demo Mode."
        })


def process_payment(request, booking_id):
    """Verify Razorpay payment signature."""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        payment = get_object_or_404(Payment, booking=booking)

        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # If it's a demo payment (no razorpay params)
        if not razorpay_payment_id:
            payment.payment_status = 'completed'
            payment.save()
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()
            return redirect('payments:payment_success', booking_id=booking.id)

        # Verify real Razorpay signature
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            payment.payment_status = 'completed'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()

            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()

            # Optional Email Notification
            try:
                send_mail(
                    "Service Booking Confirmed",
                    f"Your booking for {booking.service.title} has been confirmed. Payment received.",
                    settings.EMAIL_HOST_USER,
                    [booking.user.email, 'vedantrana0930@gmail.com'],
                    fail_silently=True,
                )
            except Exception:
                pass

            return redirect('payments:payment_success', booking_id=booking.id)

        except Exception as e:
            print(f"Payment Verification Failed: {e}")
            payment.payment_status = 'failed'
            payment.save()
            return redirect('payments:payment_failed')

    return redirect('payments:checkout', booking_id=booking_id)


def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    payment = Payment.objects.filter(booking=booking).first()
    return render(request, 'payments/success.html', {
        'booking': booking,
        'payment': payment,
    })


def payment_failed(request):
    return render(request, 'payments/failed.html')


@csrf_exempt
def razorpay_webhook(request):
    return HttpResponse("Webhook received")