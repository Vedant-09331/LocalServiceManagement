from django.db import models
from django.conf import settings
from services.models import Service


class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='vendors', null=True, blank=True)

    phone = models.CharField(max_length=15)
    experience = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to='vendors/', null=True, blank=True)
    bio = models.TextField(blank=True, default='')

    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    rating = models.FloatField(default=0)
    total_jobs = models.IntegerField(default=0)
    total_earnings = models.FloatField(default=0)

    def __str__(self):
        return self.user.email

    @property
    def get_display_profile_image(self):
        if self.profile_image:
            try:
                if self.profile_image.storage.exists(self.profile_image.name):
                    return self.profile_image.url
            except Exception:
                pass
        return f"{settings.STATIC_URL}images/services/default_services.jpg"