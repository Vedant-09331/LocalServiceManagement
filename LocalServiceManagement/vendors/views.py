from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from services.forms import ServiceForm

from .models import Vendor
from .forms import VendorRegisterForm, VendorProfileForm
from bookings.models import Booking
from services.models import Service, Review
from payments.models import Payment


def _get_vendor_or_redirect(request):
    """Helper: get vendor for the current user or redirect to register."""
    try:
        return Vendor.objects.get(user=request.user), None
    except Vendor.DoesNotExist:
        return None, redirect('vendors:vendor_register')


# ── Register ───────────────────────────────────────────────────────────────────

@login_required
def vendor_register(request):
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
            profile_image=profile_image,
        )

        messages.success(request, "Vendor profile created successfully!")
        return redirect('vendors:vendor_dashboard')

    return render(request, 'vendors/register.html')


# ── Dashboard ──────────────────────────────────────────────────────────────────

@login_required
def vendor_dashboard(request):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    bookings = Booking.objects.filter(vendor=vendor).select_related('user', 'service')
    total_bookings = bookings.count()
    completed_bookings = bookings.filter(status='completed').count()
    pending_bookings = bookings.filter(status='pending').count()
    confirmed_bookings = bookings.filter(status='confirmed').count()

    # Services this vendor owns
    my_services = Service.objects.filter(vendor=request.user)

    # Reviews for vendor's services
    reviews = Review.objects.filter(service__vendor=request.user).select_related('user', 'service').order_by('-created_at')[:5]
    reviews_count = Review.objects.filter(service__vendor=request.user).count()

    # Earnings from completed payments
    payments = Payment.objects.filter(booking__vendor=vendor, payment_status='completed')
    total_earnings_computed = payments.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'vendors/dashboard.html', {
        'vendor': vendor,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'my_services': my_services,
        'recent_reviews': reviews,
        'reviews_count': reviews_count,
        'total_earnings_computed': total_earnings_computed,
    })


# ── Profile ────────────────────────────────────────────────────────────────────

@login_required
def vendor_profile(request):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    if request.method == 'POST':
        form = VendorProfileForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            # also update first/last name if provided
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            if first_name or last_name:
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('vendors:vendor_profile')
    else:
        form = VendorProfileForm(instance=vendor)

    return render(request, 'vendors/profile.html', {'vendor': vendor, 'form': form})


# ── Bookings ───────────────────────────────────────────────────────────────────

@login_required
def vendor_bookings(request):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    status_filter = request.GET.get('status', '')
    bookings = Booking.objects.filter(vendor=vendor).select_related('user', 'service')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'vendors/bookings.html', {
        'bookings': bookings,
        'vendor': vendor,
        'status_filter': status_filter,
    })


@login_required
def accept_booking(request, booking_id):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)
    booking.status = 'confirmed'
    booking.save()
    messages.success(request, "Booking accepted successfully.")
    return redirect('vendors:vendor_dashboard')


@login_required
def reject_booking(request, booking_id):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, "Booking declined.")
    return redirect('vendors:vendor_dashboard')


@login_required
def complete_booking(request, booking_id):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    booking = get_object_or_404(Booking, id=booking_id, vendor=vendor)
    booking.status = 'completed'
    booking.save()

    vendor.total_jobs += 1
    vendor.save()

    messages.success(request, "Booking marked as completed.")
    return redirect('vendors:vendor_dashboard')


# ── Earnings ───────────────────────────────────────────────────────────────────

@login_required
def vendor_earnings(request):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    payments = Payment.objects.filter(
        booking__vendor=vendor
    ).select_related('booking__user', 'booking__service').order_by('-created_at')

    total_earned = payments.filter(payment_status='completed').aggregate(total=Sum('amount'))['total'] or 0
    pending_amount = payments.filter(payment_status='pending').aggregate(total=Sum('amount'))['total'] or 0
    total_jobs = Booking.objects.filter(vendor=vendor, status='completed').count()

    return render(request, 'vendors/earnings.html', {
        'vendor': vendor,
        'payments': payments,
        'total_earned': total_earned,
        'pending_amount': pending_amount,
        'total_jobs': total_jobs,
    })


# ── Reviews ────────────────────────────────────────────────────────────────────

@login_required
def vendor_reviews(request):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    reviews = Review.objects.filter(
        service__vendor=request.user
    ).select_related('user', 'service').order_by('-created_at')

    total_reviews = reviews.count()
    avg_rating = 0
    if total_reviews:
        avg_rating = round(sum(r.rating for r in reviews) / total_reviews, 1)

    return render(request, 'vendors/reviews.html', {
        'vendor': vendor,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
    })


# ── My Services ────────────────────────────────────────────────────────────────

@login_required
def vendor_my_services(request):
    vendor, redir = _get_vendor_or_redirect(request)
    if redir:
        return redir

    services = Service.objects.filter(vendor=request.user)
    return render(request, 'vendors/my_services.html', {
        'vendor': vendor,
        'services': services,
    })

def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.vendor = request.user   # 🔥 IMPORTANT
            service.save()
            return redirect('vendor_services')
    else:
        form = ServiceForm()

    return render(request, 'vendors/add_service.html', {'form': form})