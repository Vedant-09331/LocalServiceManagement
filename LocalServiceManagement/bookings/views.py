from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking
from services.models import Service, Review
from professionals.models import Professional
from vendors.models import Vendor


# Book a service
@login_required
def book_service(request, id):

    service = get_object_or_404(Service, id=id)
    reviews = Review.objects.filter(service=service)

    # Pre-fetch the professional so we can show it on the page
    professional = Professional.objects.filter(service=service).first()

    if request.method == "POST":
        booking_date = request.POST.get("booking_date")
        booking_time = request.POST.get("booking_time")
        address = request.POST.get("address")

        if not booking_date or not address:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'bookings/book_service.html', {
                'service': service,
                'professional': professional,
                'reviews': reviews,
            })


        # Resolve the vendor who offers this service
        vendor = Vendor.objects.filter(service=service).first()

        booking = Booking.objects.create(
            user=request.user,
            service=service,
            professional=professional,
            vendor=vendor,
            booking_date=booking_date,
            booking_time=booking_time if booking_time else None,
            address=address,
            status='pending',
        )

        messages.success(request, f'Your booking for {service.name} has been confirmed successfully!')
        return redirect('payments:checkout', booking_id=booking.id)

    return render(request, 'bookings/book_service.html', {
        'service': service,
        'professional': professional,
        'reviews': reviews,
    })


# User booking history
@login_required
def booking_history(request):

    bookings = Booking.objects.filter(user=request.user)

    return render(request, 'bookings/booking_history.html', {'bookings': bookings})


def bookings_home(request):
    return render(request, 'bookings/bookings_home.html')

@login_required
def confirm_booking(request, service_id, professional_id):

    service = get_object_or_404(Service, id=service_id)
    professional = get_object_or_404(Professional, id=professional_id)

    # Fetch reviews related to the service
    reviews = Review.objects.filter(service=service)

    if request.method == "POST":

        booking_date = request.POST.get("booking_date")
        address = request.POST.get("address")

        vendor = Vendor.objects.filter(service=service).first()

        booking = Booking.objects.create(
            user=request.user,
            service=service,
            professional=professional,
            vendor=vendor,
            booking_date=booking_date,
            address=address
        )

        return redirect("payments:checkout", booking_id=booking.id)

    return render(request, "bookings/confirm_booking.html", {
        "service": service,
        "professional": professional,
        "reviews": reviews
    })


def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})