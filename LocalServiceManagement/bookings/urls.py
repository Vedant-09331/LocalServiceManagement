from django.urls import path
from . import views

urlpatterns = [

    path('book/<int:id>/', views.book_service, name='book_service'),
    path('history/', views.booking_history, name='booking_history'),
    path('', views.bookings_home, name='bookings_home')

]