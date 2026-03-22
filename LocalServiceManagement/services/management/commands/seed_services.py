"""
Management command to seed the database with sample services, categories,
vendor users, vendor profiles, and professionals.

Usage:
    python manage.py seed_services
"""

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from services.models import Service, Category
from professionals.models import Professional
from vendors.models import Vendor
from core.models import User


SERVICES_DATA = [
    {
        "title": "Home Deep Cleaning",
        "name": "Home Deep Cleaning",
        "category": "Cleaning",
        "description": (
            "Complete home deep cleaning service including kitchen cleaning, "
            "bathroom sanitization, floor cleaning, and dust removal. Our team "
            "ensures a clean and hygienic living space. All equipment and "
            "cleaning products are provided by us."
        ),
        "price": 799.00,
        "city": "Mumbai",
        "location": "Mumbai, Maharashtra",
        "image_src": "home_cleaning.png",
        "professional_name": "Rajesh Kumar",
        "experience": 5,
        "professional_rating": 4.8,
    },
    {
        "title": "Plumbing Repair & Installation",
        "name": "Plumbing Repair & Installation",
        "category": "Plumbing",
        "description": (
            "Expert plumbing services including pipe repair, leak fixing, "
            "tap installation, water heater installation, and drainage "
            "solutions. Our licensed plumbers are available 7 days a week "
            "and ensure quality workmanship."
        ),
        "price": 499.00,
        "city": "Delhi",
        "location": "Delhi, NCR",
        "image_src": "plumbing.png",
        "professional_name": "Suresh Sharma",
        "experience": 8,
        "professional_rating": 4.6,
    },
    {
        "title": "Electrical Repair & Wiring",
        "name": "Electrical Repair & Wiring",
        "category": "Electrical",
        "description": (
            "Professional electrical services including wiring, switchboard "
            "replacement, fan installation, MCB fixing, and short circuit "
            "repair. All our electricians are certified and follow safety "
            "protocols strictly."
        ),
        "price": 399.00,
        "city": "Bangalore",
        "location": "Bangalore, Karnataka",
        "image_src": "electrical.png",
        "professional_name": "Amit Patel",
        "experience": 6,
        "professional_rating": 4.7,
    },
    {
        "title": "Home Salon & Beauty Service",
        "name": "Home Salon & Beauty Service",
        "category": "Beauty & Wellness",
        "description": (
            "Luxury home salon services including haircut, blow-dry, facial, "
            "waxing, threading, and manicure/pedicure. Get salon-quality "
            "beauty treatments from the comfort of your home. All products "
            "used are premium and hygienic."
        ),
        "price": 999.00,
        "city": "Mumbai",
        "location": "Mumbai, Maharashtra",
        "image_src": "salon_beauty.png",
        "professional_name": "Priya Mehta",
        "experience": 7,
        "professional_rating": 4.9,
    },
    {
        "title": "Pest Control Treatment",
        "name": "Pest Control Treatment",
        "category": "Pest Control",
        "description": (
            "Comprehensive pest control services for cockroaches, ants, "
            "bedbugs, mosquitoes, termites, and rodents. We use safe, "
            "government-approved chemicals. Treatment covers your entire "
            "home and is effective for up to 3 months."
        ),
        "price": 1299.00,
        "city": "Hyderabad",
        "location": "Hyderabad, Telangana",
        "image_src": "pest_control.png",
        "professional_name": "Venkat Rao",
        "experience": 10,
        "professional_rating": 4.5,
    },
    {
        "title": "Carpentry & Furniture Repair",
        "name": "Carpentry & Furniture Repair",
        "category": "Carpentry",
        "description": (
            "Skilled carpentry services including furniture assembly, "
            "door/window repair, wardrobe fitting, wooden flooring, and "
            "custom woodwork. Our experienced carpenters deliver precise "
            "and durable results for all your wooden work needs."
        ),
        "price": 599.00,
        "city": "Pune",
        "location": "Pune, Maharashtra",
        "image_src": "carpentry.png",
        "professional_name": "Mohan Das",
        "experience": 9,
        "professional_rating": 4.6,
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample service categories, vendors, professionals, and services."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting service seeding..."))

        # --- Create/get vendor user ---
        vendor_user, created = User.objects.get_or_create(
            email="vendor@localservices.com",
            defaults={
                "role": "vendor",
                "is_active": True,
                "is_staff": False,
                "is_admin": False,
            },
        )
        if created:
            vendor_user.set_password("Vendor@1234")
            vendor_user.save()
            self.stdout.write(self.style.SUCCESS("  ✔ Created vendor user: vendor@localservices.com"))
        else:
            self.stdout.write("  • Vendor user already exists.")

        # --- Create/get Vendor profile ---
        vendor_profile, created = Vendor.objects.get_or_create(
            user=vendor_user,
            defaults={
                "phone": "9876543210",
                "address": "123 Service Lane, Mumbai, Maharashtra",
                "is_verified": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("  ✔ Created Vendor profile."))
        else:
            self.stdout.write("  • Vendor profile already exists.")

        # --- Media directory ---
        media_services_dir = os.path.join(settings.MEDIA_ROOT, "services")
        os.makedirs(media_services_dir, exist_ok=True)

        # Source images directory (generated images placed here by seed script)
        brain_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "service_images",
        )

        # --- Seed each service ---
        for data in SERVICES_DATA:
            # Category
            category, _ = Category.objects.get_or_create(name=data["category"])

            # Copy image if available
            image_relative_path = None
            src_image = os.path.join(brain_dir, data["image_src"])
            if os.path.exists(src_image):
                dest_filename = data["image_src"]
                dest_path = os.path.join(media_services_dir, dest_filename)
                shutil.copy2(src_image, dest_path)
                image_relative_path = f"services/{dest_filename}"
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  ⚠ Image not found for {data['title']}: {src_image}"
                    )
                )

            # Service (use get_or_create on title+vendor to avoid duplicates)
            service, created = Service.objects.get_or_create(
                title=data["title"],
                vendor=vendor_user,
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "price": data["price"],
                    "city": data["city"],
                    "location": data["location"],
                    "category": category,
                    "image": image_relative_path or "",
                    "rating": 0,
                    "rating_count": 0,
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✔ Created service: {data['title']} — ₹{data['price']}")
                )
            else:
                self.stdout.write(f"  • Service already exists: {data['title']}")

            # Professional linked to service
            professional, pro_created = Professional.objects.get_or_create(
                name=data["professional_name"],
                service=service,
                defaults={
                    "experience": data["experience"],
                    "rating": data["professional_rating"],
                    "jobs_completed": 0,
                },
            )
            if pro_created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"    ✔ Created professional: {data['professional_name']}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "\n✅ Seeding complete! Services, professionals, and vendor created successfully."
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "  Vendor login: vendor@localservices.com / Vendor@1234"
            )
        )
