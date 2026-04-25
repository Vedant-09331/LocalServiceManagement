from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files import File
from datetime import timedelta
import os

from django.conf import settings
from core.models import User
from services.models import Category, Service, Review, Favorite
from vendors.models import Vendor
from professionals.models import Professional
from bookings.models import Booking
from payments.models import Payment


class Command(BaseCommand):
    help = "Seeds the database with example data using ONLY existing local media files. Overwrites old images."

    def handle(self, *args, **options):
        self.stdout.write("Cleaning up and seeding with LOCAL images ONLY...\n")

        # --- 1. Categories ---
        category_names = [
            'Cleaning', 'Plumbing', 'Electrical', 'AC Repair',
            'Painting', 'Carpentry', 'Pest Control', 'Beauty & Spa'
        ]
        categories = {}
        for name in category_names:
            cat, _ = Category.objects.get_or_create(name=name)
            categories[name] = cat

        # --- 2. Image Mapping (Strictly Local) ---
        image_map = {
            'Cleaning': 'home_repairement.jpg',
            'Plumbing': 'plumbering2.jpg',
            'Electrical': 'hand-drawn-electrician-cartoon-illustration_23-2151046712.avif',
            'AC Repair': 'istockphoto-1417833187-612x612_1.jpg',
            'Painting': 'images.jpg',
            'Carpentry': '2d6d0e31d02d7fc9cd2fb2310f49153c.jpg',
            'Pest Control': 'beautiful-asian-woman-many-hand-260nw-1734917243.webp',
            'Beauty & Spa': 'portrait-professional-beautician-cosmetologist-work-600nw-2620996373.webp',
        }

        # --- 3. Users ---
        vendor_user, _ = User.objects.get_or_create(email='vendor@test.com', defaults={'role': 'vendor'})

        # --- 4. Services ---
        services_data = [
            {'name': 'Premium Home Cleaning', 'category': 'Cleaning', 'price': 1499.00},
            {'name': 'Pipe Leak Repair', 'category': 'Plumbing', 'price': 799.00},
            {'name': 'Full Home Wiring', 'category': 'Electrical', 'price': 2999.00},
            {'name': 'AC Service & Gas Refill', 'category': 'AC Repair', 'price': 1299.00},
            {'name': 'Interior Wall Painting', 'category': 'Painting', 'price': 4999.00},
            {'name': 'Kitchen Cabinet Repair', 'category': 'Carpentry', 'price': 1999.00},
            {'name': 'Termite Treatment', 'category': 'Pest Control', 'price': 1599.00},
            {'name': 'Bridal Makeup Package', 'category': 'Beauty & Spa', 'price': 8999.00},
        ]

        for sdata in services_data:
            Service.objects.get_or_create(
                name=sdata['name'],
                defaults={
                    'title': sdata['name'],
                    'vendor': vendor_user,
                    'price': sdata['price'],
                    'category': categories[sdata['category']],
                    'description': f"Professional {sdata['category']} service.",
                    'rating': 4.5,
                    'rating_count': 10,
                }
            )

        self.stdout.write(self.style.SUCCESS("\nAll services seeded successfully (without images)!"))
