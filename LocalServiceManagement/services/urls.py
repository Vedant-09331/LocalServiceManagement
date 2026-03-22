from django.urls import path
from . import views

app_name = 'services'
urlpatterns = [

    path('', views.services_list, name='services_list'),
    path('add/', views.add_service, name='add_service'),
    path('vendor/', views.vendor_services, name='vendor_services'),
    path('detail/<int:service_id>/', views.service_detail, name='service_detail'),
    path('vendor/services/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('vendor/services/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('review/add/<int:service_id>/', views.add_review, name='add_review'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('favorite/toggle/<int:service_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_list, name='favorite_list'),
]
    