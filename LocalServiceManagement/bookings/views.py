from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
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
        vendor=service.vendor
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


@login_required
def write_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Only allow reviews for completed bookings
    if booking.status != 'completed':
        messages.error(request, 'You can only review a completed booking.')
        return redirect('bookings:booking_history')

    # Prevent duplicate reviews
    if Review.objects.filter(service=booking.service, user=request.user).exists():
        messages.warning(request, 'You have already reviewed this service.')
        return redirect('services:service_detail', service_id=booking.service.id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating:
            messages.error(request, 'Please select a star rating.')
            return render(request, 'bookings/write_review.html', {'booking': booking})

        rating = int(rating)
        if not (1 <= rating <= 5):
            messages.error(request, 'Rating must be between 1 and 5.')
            return render(request, 'bookings/write_review.html', {'booking': booking})

        # Create the review
        Review.objects.create(
            service=booking.service,
            user=request.user,
            rating=rating,
            comment=comment,
        )

        # Recalculate and update the service average rating
        service = booking.service
        aggregated = Review.objects.filter(service=service).aggregate(average=Avg('rating'))
        service.rating = round(aggregated['average'] or 0, 1)
        service.rating_count = Review.objects.filter(service=service).count()
        service.save()

        messages.success(request, f'Thank you! Your review for "{service.name}" has been submitted.')
        return redirect('services:service_detail', service_id=service.id)

    return render(request, 'bookings/write_review.html', {'booking': booking})