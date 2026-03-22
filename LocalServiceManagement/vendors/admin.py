from django.contrib import admin
from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['user', 'service', 'is_verified', 'rating']
    list_filter = ['is_verified', 'service']