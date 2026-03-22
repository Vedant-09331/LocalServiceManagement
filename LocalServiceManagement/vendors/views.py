from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vendor
from .forms import VendorRegisterForm
from bookings.models import Booking
from django.contrib import messages

@login_required
def vendor_register(request):
    # Check if vendor already exists
    if Vendor.objects.filter(user=request.user).exists():
        messages.warning(request, "You already have a vendor profile.")
        return redirect('vendors:vendor_dashboard')

    if request.method == 'POST':
        service = request.POST.get('service')
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        profile_image = request.FILES.get('profile_image')

        Vendor.objects.create(
            user=request.user,
            service_id=service,
            phone=phone,
            experience=experience,
            profile_image=profile_image
        )

        messages.success(request, "Vendor profile created successfully!")
        return redirect('vendors:vendor_dashboard')

    return render(request, 'vendors/register.html')


@login_required
def vendor_dashboard(request):
    # Get vendor of logged-in user
    vendor = Vendor.objects.get(user=request.user)

    # Get bookings assigned to this vendor directly
    bookings = Booking.objects.filter(vendor=vendor).select_related('user', 'service')

    # Aggregate stats
    total_bookings = bookings.count()
    completed_bookings = bookings.filter(status='completed').count()
    pending_bookings = bookings.filter(status='pending').count()

    return render(request, 'vendors/dashboard.html', {
        'vendor': vendor,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
    })


@login_required
def vendor_bookings(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    bookings = Booking.objects.filter(professional=vendor)

    return render(request, 'vendors/bookings.html', {'bookings': bookings})


@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'confirmed'
    booking.save()
    messages.success(request, "Booking accepted successfully.")
    return redirect('vendors:vendor_dashboard')


@login_required
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'completed'
    booking.save()

    # Update vendor job count
    vendor = get_object_or_404(Vendor, user=request.user)
    vendor.total_jobs += 1
    vendor.save()

    messages.success(request, "Booking marked as completed.")
    return redirect('vendors:vendor_dashboard')

def update_booking_status(request, booking_id, action):
    booking = Booking.objects.get(id=booking_id)
    if action == 'accept':
        booking.status = 'Accepted'
    elif action == 'reject':
        booking.status = 'Rejected'
    booking.save()
    # Send notification to customer after saving
    send_notification(
        booking.customer.email, 
        f"Your booking for {booking.service.name} has been {booking.status}"
    )

    return redirect('vendor_bookings')