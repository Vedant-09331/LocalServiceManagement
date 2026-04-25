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


def _deduplicated_upload(instance, filename, upload_dir):
    """
    Return a path for the uploaded image.
    If a file with the same MD5 hash already exists anywhere inside MEDIA_ROOT,
    reuse that path instead of saving a duplicate.
    """
    if not instance.image:
        return os.path.join(upload_dir, filename)

    file_hash = _file_md5(instance.image.file)

    # Walk the entire media tree looking for an identical file
    media_root = str(settings.MEDIA_ROOT)
    for dirpath, _dirnames, filenames in os.walk(media_root):
        for existing_name in filenames:
            existing_path = os.path.join(dirpath, existing_name)
            try:
                with open(existing_path, 'rb') as f:
                    existing_hash = hashlib.md5(f.read()).hexdigest()
                if existing_hash == file_hash:
                    # Return the *relative* path from MEDIA_ROOT
                    return os.path.relpath(existing_path, media_root).replace('\\', '/')
            except (IOError, OSError):
                continue

    # No duplicate found — save normally
    return os.path.join(upload_dir, filename)


def service_image_path(instance, filename):
    return _deduplicated_upload(instance, filename, 'services/')


def gallery_image_path(instance, filename):
    return _deduplicated_upload(instance, filename, 'service_gallery/')


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

def average_rating(self):
    return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'service')  # prevents duplicate favorites

    def __str__(self):
        return f"{self.user} ❤️ {self.service}"