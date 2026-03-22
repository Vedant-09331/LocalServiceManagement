from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import UserLoginForm, UserSignupForm
from services.models import Service, Category
from bookings.models import Booking   # ✅ IMPORTANT


# ---------------- HOME ---------------- #
def home(request):
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    category_id = request.GET.get('category', '')

    services = Service.objects.all()

    if query:
        services = services.filter(name__icontains=query) | services.filter(description__icontains=query)

    if city:
        services = services.filter(city__icontains=city)

    if category_id:
        services = services.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, "core/home.html", {
        "services": services[:8],
        "query": query,
        "city": city,
        "category_id": category_id,
        "categories": categories
    })


# ---------------- SIGNUP ---------------- #
def usersignupView(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('core:login')
    else:
        form = UserSignupForm()

    return render(request, 'core/signup.html', {'form': form})


# ---------------- LOGIN ---------------- #
def userloginView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)

            if user:
                login(request, user)

                # ROLE BASED REDIRECT
                if user.role == 'admin':
                    return redirect('core:admin_dashboard')
                elif user.role == 'vendor':
                    return redirect('core:vendor_dashboard')
                else:
                    return redirect('core:home')

            messages.error(request, 'Invalid email or password')
    else:
        form = UserLoginForm()

    return render(request, 'core/login.html', {'form': form})


# ---------------- ROLE REDIRECT ---------------- #
@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return redirect('core:admin_dashboard')
    elif request.user.role == 'vendor':
        return redirect('core:vendor_dashboard')
    return redirect('core:user_dashboard')


# ---------------- USER DASHBOARD ---------------- #
@login_required
def userDashboard(request):
    if request.user.role != 'user':
        return redirect('core:login')

    bookings = Booking.objects.filter(user=request.user).select_related('service', 'vendor').order_by('-created_at')

    upcoming_bookings = bookings.filter(status__in=['pending', 'confirmed'])
    past_bookings     = bookings.filter(status='completed')
    recent_bookings   = bookings[:5]

    # Services for Browse panel
    services = Service.objects.all().select_related('category')[:6]
    categories = Category.objects.all()

    return render(request, 'core/user_dashboard.html', {
        'bookings': bookings,
        'upcoming_count': upcoming_bookings.count(),
        'past_count':     past_bookings.count(),
        'upcoming_bookings': upcoming_bookings[:5],
        'recent_bookings':   recent_bookings,
        'services':   services,
        'categories': categories,
    })


# ---------------- ADMIN DASHBOARD ---------------- #
@login_required
def adminDashboard(request):
    if request.user.role != 'admin':
        return redirect('core:login')

    users_count = Booking.objects.count()
    services_count = Service.objects.count()

    return render(request, 'core/admin_dashboard.html', {
        'users_count': users_count,
        'services_count': services_count
    })


# ---------------- VENDOR DASHBOARD 🔥 ---------------- #
@login_required
def vendorDashboard(request):
    # 🔒 सुरक्षा: only vendor
    if request.user.role != 'vendor':
        return redirect('core:login')

    user = request.user

    # 📦 All bookings of this vendor
    bookings = Booking.objects.filter(
        professional=user
    ).order_by('-created_at')

    # 📊 Stats
    total_bookings = bookings.count()
    pending = bookings.filter(status='pending').count()
    completed = bookings.filter(status='completed').count()

    # 💰 Earnings (only completed bookings)
    earnings = bookings.filter(status='completed').aggregate(
        total=Sum('service__price')
    )['total'] or 0

    # ⭐ Rating (average of all reviews)
    rating = Review.objects.filter(
        service__vendor=user
    ).aggregate(
        avg=Avg('rating')
    )['avg'] or 0

    # 🛠 Vendor services
    services = Service.objects.filter(vendor=user)

    # 📅 Recent bookings (for dashboard table)
    recent_bookings = bookings[:5]

    return render(request, 'core/vendor_dashboard.html', {
        'bookings': bookings,
        'recent_bookings': recent_bookings,

        'total_bookings': total_bookings,
        'pending': pending,
        'completed': completed,

        'earnings': earnings,
        'rating': round(rating, 1),

        'services': services
    })


# ---------------- UPDATE BOOKING STATUS 🔥 ---------------- #
@login_required
def updateBookingStatus(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # SECURITY CHECK
    if booking.professional != request.user:
        messages.error(request, "Unauthorized access")
        return redirect('core:vendor_dashboard')

    if request.method == "POST":
        status = request.POST.get('status')

        if status in ['accepted', 'rejected', 'completed']:
            booking.status = status
            booking.save()
            messages.success(request, "Booking updated successfully!")

    return redirect('core:vendor_dashboard')


# ---------------- LOGOUT ---------------- #
def userlogoutView(request):
    logout(request)
    return redirect('core:login')


# ---------------- VENDOR PROFILE ---------------- #
def vendor_profile(request):
    if request.user.role != 'vendor':
        return redirect('core:login')

    user = request.user

    if request.method == 'POST':
        user.bio = request.POST.get('bio')
        
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')

        user.save()
        messages.success(request, "Profile updated successfully")

    return render(request, 'core/vendor_profile.html')