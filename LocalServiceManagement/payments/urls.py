from django.urls import path
from . import views

urlpatterns = [
    path("checkout/<int:booking_id>/", views.checkout, name="checkout"),
    path("payment-success/<int:booking_id>/", views.payment_success, name="payment_success"),
    path("payment-failed/", views.payment_failed, name="payment_failed"),
    path("webhook/razorpay/", views.razorpay_webhook, name="razorpay_webhook"),
]