from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/<int:booking_id>/", views.checkout, name="checkout"),
    path("process-payment/<int:booking_id>/", views.process_payment, name="process_payment"),
    path("success/<int:booking_id>/", views.payment_success, name="payment_success"),
    path("failed/", views.payment_failed, name="payment_failed"),
]