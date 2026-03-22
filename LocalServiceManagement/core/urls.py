from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.usersignupView, name='signup'),
    path('login/', views.userloginView, name='login'),
    path('logout/', views.userlogoutView, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-dashboard/', views.userDashboard, name='user_dashboard'),
    path('admin-dashboard/', views.adminDashboard, name='admin_dashboard'),
    path('vendor/profile/',views.vendor_profile, name='vendor_profile'),
    path('update-booking/<int:booking_id>/<str:status>/', views.updateBookingStatus, name='update_booking_status'),
]