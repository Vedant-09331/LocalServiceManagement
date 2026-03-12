from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from urllib3 import request
from bookings.models import Booking

def payment_page(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":

        booking.payment_status = "paid"
        booking.status = "confirmed"
        booking.save()

        # SEND EMAIL TO USER
        send_mail(
            "Service Booking Confirmed",
            f"Your booking for {booking.service.name} has been confirmed successfully.",
            "admin@localservices.com",
            [booking.user.email],
        )

        return redirect("booking_success", booking.id)

    return render(request, "payments/payment_page.html", {
        "booking": booking
    })

def checkout(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    return render(request, "payments/checkout.html", {
        "booking": booking
    })
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    return render(request, "payments/success.html", {
        "booking": booking
    })


def payment_failed(request):
    return render(request, "payments/failed.html")


def razorpay_webhook(request):
    return HttpResponse("Webhook received")     