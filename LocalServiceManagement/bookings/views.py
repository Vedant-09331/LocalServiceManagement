from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking
from services.models import Service


# Book a service
from django.shortcuts import render, redirect, get_object_or_404
from .forms import BookingForm
from .models import Booking
from services.models import Service
from django.contrib.auth.decorators import login_required


@login_required
def book_service(request, id):

    service = get_object_or_404(Service, id=id)

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)

            booking.user = request.user
            booking.service = service
            booking.status = 'Accepted'  # Set status to Accepted immediately

            booking.save()

            messages.success(request, f'Your booking for {service.name} has been confirmed successfully!')
            return redirect('booking_history')

    else:
        form = BookingForm()

    return render(request, 'bookings/book_service.html', {
        'form': form,
        'service': service
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

    if request.method == "POST":

        booking_date = request.POST.get("booking_date")
        address = request.POST.get("address")

        booking = Booking.objects.create(
            user=request.user,
            service=service,
            professional=professional,
            booking_date=booking_date,
            address=address
        )

        return redirect("payment_page", booking.id)

    return render(request, "bookings/confirm_booking.html", {
        "service": service,
        "professional": professional
    })