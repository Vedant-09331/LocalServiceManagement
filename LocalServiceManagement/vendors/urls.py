from django.urls import path
from . import views
app_name = 'vendors'
urlpatterns = [
    path('register/', views.vendor_register, name='vendor_register'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('bookings/', views.vendor_bookings, name='vendor_bookings'),

    path('accept/<int:booking_id>/', views.accept_booking, name='accept_booking'),
    path('complete/<int:booking_id>/', views.complete_booking, name='complete_booking'),
]