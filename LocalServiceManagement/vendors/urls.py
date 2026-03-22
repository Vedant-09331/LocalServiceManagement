from django.urls import path
from . import views

app_name = 'vendors'

urlpatterns = [
    # Registration & Dashboard
    path('register/', views.vendor_register, name='vendor_register'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),

    # Profile
    path('profile/', views.vendor_profile, name='vendor_profile'),

    # Services
    path('services/', views.vendor_my_services, name='vendor_my_services'),

    # Bookings
    path('bookings/', views.vendor_bookings, name='vendor_bookings'),
    path('accept/<int:booking_id>/', views.accept_booking, name='accept_booking'),
    path('reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('complete/<int:booking_id>/', views.complete_booking, name='complete_booking'),

    # Earnings
    path('earnings/', views.vendor_earnings, name='vendor_earnings'),

    # Reviews
    path('reviews/', views.vendor_reviews, name='vendor_reviews'),
]