from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [

    path('book/<int:id>/', views.book_service, name='book_service'),
    path('confirm/<int:service_id>/<int:professional_id>/', views.confirm_booking, name='confirm_booking'),
    path('history/', views.booking_history, name='booking_history'),
    path('', views.bookings_home, name='bookings_home'),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path('review/<int:booking_id>/', views.write_review, name='write_review'),
]