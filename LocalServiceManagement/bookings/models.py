from django.db import models
from django.utils import timezone
from core.models import User
from services.models import Service
from professionals.models import Professional

class Booking(models.Model):
    """
    Represents a booking/appointment for a service.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_reviews')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    professional = models.ForeignKey(Professional, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateField(default=timezone.now)
    booking_time = models.TimeField(null=True, blank=True)
    address = models.TextField(default='')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, related_name='bookings', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['booking_date']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.service.title} ({self.status})"

class Review(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.rating}"