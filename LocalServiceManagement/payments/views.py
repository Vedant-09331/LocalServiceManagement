from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from bookings.models import Booking
from .models import Payment

from django.shortcuts import render, redirect, get_object_or_404
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

        # For now, simulate payment success
        # In production, integrate with actual payment gateway
        payment.payment_status = 'completed'
        payment.save()

        # Update booking status
        booking.payment_status = 'paid'
        booking.status = 'confirmed'
        booking.save()

        # Send confirmation email
        send_mail(
            "Service Booking Confirmed",
            f"Your booking for {booking.service.title} has been confirmed successfully. Payment received.",
            "admin@localservices.com",
            [booking.user.email],
        )

        return redirect('payments:payment_success', booking_id=booking.id)

    return redirect('payments:checkout', booking_id=booking_id)

def payment_success(request, booking_id):
    # Get the booking object or return 404 if not found
    booking = get_object_or_404(Booking, id=booking_id)

    # Update booking payment status if needed
    booking.payment_status = 'Paid'
    booking.save()

    # Send confirmation email if user has an email
    if booking.user and booking.user.email:
        send_mail(
            subject='Booking Confirmation',
            message=f'Hi {booking.user.email}, your booking #{booking.id} was successful!',
            from_email='your-email@gmail.com',
            recipient_list=[booking.user.email],
            fail_silently=False,  # set True if you want to ignore email errors
        )

    # Redirect to a success page or dashboard
    return render(request, 'payments/success.html', {
    'booking': booking,
    'user_name': booking.user.email,  # or booking.user.full_name if you have it
})

def payment_failed(request):
    return render(request, 'payments/failed.html')

@csrf_exempt
def razorpay_webhook(request):
    # Placeholder for future webhook implementation
    return HttpResponse("Webhook received")