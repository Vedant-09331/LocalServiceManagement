from django.urls import path
from . import views
urlpatterns = [

    path('', views.services_list, name='services_list'),
    path('add/', views.add_service, name='add_service'),
    path('vendor/', views.vendor_services, name='vendor_services'),
    path('detail/<int:service_id>/', views.service_detail, name='service_detail'),
]