from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from bookings.models import Booking
from .models import Payment


def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={"amount": booking.service.price}
    )

    if request.method == "POST":
        payment.payment_status = "completed"
        payment.save()

        return redirect("payments:payment_success", booking_id=booking.id)

    return render(request, "payments/checkout.html", {
        "booking": booking,
        "payment": payment
    })


def process_payment(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        payment = get_object_or_404(Payment, booking=booking)

        payment.payment_status = 'completed'
        payment.save()

        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.save()

        # ✅ DEBUG EMAIL
        user_email = booking.user.email.strip() if booking.user.email else None
        print("User email is:", user_email)

        # ✅ SEND EMAIL ONLY IF VALID
        if user_email:
            try:
                send_mail(
                    "Service Booking Confirmed",
                    f"Your booking for {booking.service.title} has been confirmed successfully. Payment received.",
                    settings.EMAIL_HOST_USER,
                    ['vedantrana0930@gmail.com'],
                    fail_silently=False,
                )
                print("Email sent successfully ✅")
            except Exception as e:
                print("Email failed ❌:", e)
        else:
            print("No email found ❌")

        return redirect('payments:payment_success', booking_id=booking.id)

    return redirect('payments:checkout', booking_id=booking_id)


def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    return render(request, 'payments/success.html', {
        'booking': booking,
        'user_name': booking.user.email,
    })


def payment_failed(request):
    return render(request, 'payments/failed.html')


@csrf_exempt
def razorpay_webhook(request):
    return HttpResponse("Webhook received")