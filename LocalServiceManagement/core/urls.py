from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.usersignupView, name='signup'),
    path('login/', views.userloginView, name='login'),
    path('logout/', views.userlogoutView, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-dashboard/', views.userDashboard, name='user_dashboard'),
    path('admin-dashboard/', views.adminDashboard, name='admin_dashboard'),
    path('vendor-dashboard/', views.vendorDashboard, name='vendor_dashboard'),
]