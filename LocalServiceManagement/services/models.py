import hashlib
import os

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import default_storage


def _file_md5(file_obj):
    """Calculate the MD5 hash of an uploaded file."""
    md5 = hashlib.md5()
    file_obj.seek(0)
    for chunk in file_obj.chunks():
        md5.update(chunk)
    file_obj.seek(0)
    return md5.hexdigest()


def service_image_path(instance, filename):
    return f'services/{filename}'


def gallery_image_path(instance, filename):
    return f'service_gallery/{filename}'


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Service(models.Model):
    title = models.CharField(max_length=200)
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, default='')
    description = models.TextField(default='')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=service_image_path, blank=True, null=True)
    rating = models.FloatField(default=0)  # average rating
    rating_count = models.PositiveIntegerField(default=0)  # number of ratings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title if self.title else self.name

    @property
    def get_display_image(self):
        if self.image:
            return self.image.url

        # 2. Fallback to category-based static images
        mapping = {
            'cleaning': 'cleaning.jpg',
            'plumbing': 'plumbing.jpg',
            'electrical': 'electrical.avif',
            'ac repair': 'ac_repair.jpg',
            'painting': 'painting.jpg',
            'carpentry': 'carpentry.jpg',
            'pest control': 'pest_control.webp',
            'beauty & spa': 'beauty_spa.webp',
        }
        
        category_name = self.category.name.lower() if self.category else ''
        file_name = mapping.get(category_name)
        
        if file_name:
            return f"{settings.STATIC_URL}images/services/{file_name}"
            
        # 3. Last resort: Dynamic placeholder
        import urllib.parse
        encoded_name = urllib.parse.quote(self.name or self.title or 'Service')
        return f"https://placehold.co/600x400?text={encoded_name}"

    def average_rating(self):
        from django.db.models import Avg
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0



class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.service}"


class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    experience = models.IntegerField()
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email


class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=gallery_image_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.service.title}"

    class Meta:
        ordering = ['-created_at']


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'service')  # prevents duplicate favorites

    def __str__(self):
        return f"{self.user} ❤️ {self.service}"