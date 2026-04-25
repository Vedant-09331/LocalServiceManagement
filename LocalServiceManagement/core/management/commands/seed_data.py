from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from datetime import timedelta
import random
import requests

from core.models import User
from services.models import Category, Service, Review, Favorite
from vendors.models import Vendor
from professionals.models import Professional
from bookings.models import Booking
from payments.models import Payment


class Command(BaseCommand):
    help = "Seeds the database with example data and real images from Unsplash."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database with example data and images...\n")

        # --- 1. Users ---
        user, _ = User.objects.get_or_create(
            email='user@test.com',
            defaults={'role': 'user'}
        )
        user.set_password('testpassword123')
        user.first_name = 'Rahul'
        user.last_name = 'Sharma'
        user.save()

        user2, _ = User.objects.get_or_create(
            email='user2@test.com',
            defaults={'role': 'user'}
        )
        user2.set_password('testpassword123')
        user2.first_name = 'Priya'
        user2.last_name = 'Singh'
        user2.save()

        vendor_user, _ = User.objects.get_or_create(
            email='vendor@test.com',
            defaults={'role': 'vendor'}
        )
        vendor_user.set_password('testpassword123')
        vendor_user.first_name = 'Amit'
        vendor_user.last_name = 'Patel'
        vendor_user.save()

        vendor_user2, _ = User.objects.get_or_create(
            email='vendor2@test.com',
            defaults={'role': 'vendor'}
        )
        vendor_user2.set_password('testpassword123')
        vendor_user2.first_name = 'Sanjay'
        vendor_user2.last_name = 'Kumar'
        vendor_user2.save()

        admin_user, _ = User.objects.get_or_create(email='admin@test.com')
        admin_user.set_password('testpassword123')
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'User'
        admin_user.role = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        self.stdout.write(self.style.SUCCESS("Users created"))

        # --- 2. Categories ---
        category_names = [
            'Cleaning', 'Plumbing', 'Electrical', 'AC Repair',
            'Painting', 'Carpentry', 'Pest Control', 'Beauty & Spa'
        ]
        categories = {}
        for name in category_names:
            cat, _ = Category.objects.get_or_create(name=name)
            categories[name] = cat

        self.stdout.write(self.style.SUCCESS("Categories created"))

        # --- 3. Services with Images ---
        services_data = [
            {
                'name': 'Premium Home Cleaning',
                'title': 'Premium Home Cleaning',
                'description': 'Deep cleaning for your entire home including kitchen, bathrooms, bedrooms, and living areas. Our team uses eco-friendly products.',
                'price': 1499.00,
                'category': 'Cleaning',
                'vendor': vendor_user,
                'rating': 4.5,
                'rating_count': 12,
                'img_query': 'home-cleaning'
            },
            {
                'name': 'Pipe Leak Repair',
                'title': 'Pipe Leak Repair',
                'description': 'Expert plumbing service for leaking pipes, tap repairs, and drainage solutions. Available 24/7 for emergencies.',
                'price': 799.00,
                'category': 'Plumbing',
                'vendor': vendor_user,
                'rating': 4.2,
                'rating_count': 8,
                'img_query': 'plumbing'
            },
            {
                'name': 'Full Home Wiring',
                'title': 'Full Home Wiring',
                'description': 'Complete electrical wiring, switchboard installation, and safety inspection for your home or office.',
                'price': 2999.00,
                'category': 'Electrical',
                'vendor': vendor_user,
                'rating': 4.7,
                'rating_count': 15,
                'img_query': 'electrical-work'
            },
            {
                'name': 'AC Service & Gas Refill',
                'title': 'AC Service & Gas Refill',
                'description': 'AC deep cleaning, gas refill, and performance check. Covers split and window units.',
                'price': 1299.00,
                'category': 'AC Repair',
                'vendor': vendor_user2,
                'rating': 4.3,
                'rating_count': 10,
                'img_query': 'air-conditioner'
            },
            {
                'name': 'Interior Wall Painting',
                'title': 'Interior Wall Painting',
                'description': 'Professional wall painting with premium Asian Paints. Covers 1BHK to 3BHK apartments.',
                'price': 4999.00,
                'category': 'Painting',
                'vendor': vendor_user2,
                'rating': 4.6,
                'rating_count': 7,
                'img_query': 'painting-wall'
            },
            {
                'name': 'Kitchen Cabinet Repair',
                'title': 'Kitchen Cabinet Repair',
                'description': 'Custom carpentry for kitchen cabinets, wardrobes, and wooden furniture repair.',
                'price': 1999.00,
                'category': 'Carpentry',
                'vendor': vendor_user2,
                'rating': 4.0,
                'rating_count': 5,
                'img_query': 'carpentry'
            },
            {
                'name': 'Termite Treatment',
                'title': 'Termite Treatment',
                'description': 'Complete pest control for cockroaches, termites, bed bugs, and rodents. Safe for children and pets.',
                'price': 1599.00,
                'category': 'Pest Control',
                'vendor': vendor_user,
                'rating': 4.4,
                'rating_count': 9,
                'img_query': 'pest-control'
            },
            {
                'name': 'Bridal Makeup Package',
                'title': 'Bridal Makeup Package',
                'description': 'Full bridal makeup with HD finish, hairstyling, draping, and touch-ups. Premium products used.',
                'price': 8999.00,
                'category': 'Beauty & Spa',
                'vendor': vendor_user2,
                'rating': 4.8,
                'rating_count': 20,
                'img_query': 'makeup-bridal'
            },
        ]

        created_services = []
        for sdata in services_data:
            svc, created = Service.objects.get_or_create(
                name=sdata['name'],
                vendor=sdata['vendor'],
                defaults={
                    'title': sdata['title'],
                    'description': sdata['description'],
                    'price': sdata['price'],
                    'category': categories[sdata['category']],
                    'rating': sdata['rating'],
                    'rating_count': sdata['rating_count'],
                }
            )
            
            # Add image if it doesn't have one
            if created or not svc.image:
                try:
                    img_url = f"https://source.unsplash.com/featured/800x600?{sdata['img_query']}"
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        file_name = f"{sdata['img_query']}_{random.randint(100,999)}.jpg"
                        svc.image.save(file_name, ContentFile(response.content), save=True)
                        self.stdout.write(f"  + Added image for {svc.name}")
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"  ! Could not fetch image for {svc.name}: {e}"))
            
            created_services.append(svc)

        self.stdout.write(self.style.SUCCESS(f"{len(created_services)} Services created"))

        # --- 4. Vendor Profiles ---
        v1, _ = Vendor.objects.get_or_create(
            user=vendor_user,
            defaults={
                'phone': '9876543210',
                'experience': 5,
                'bio': 'Expert in home cleaning, plumbing, and electrical services. 5+ years experience.',
                'is_verified': True,
                'is_available': True,
                'rating': 4.5,
                'total_jobs': 45,
                'total_earnings': 67500.00,
                'service': created_services[0],
            }
        )
        v2, _ = Vendor.objects.get_or_create(
            user=vendor_user2,
            defaults={
                'phone': '9876543211',
                'experience': 3,
                'bio': 'Specialized in AC repair, painting, and carpentry. Quality work guaranteed.',
                'is_verified': True,
                'is_available': True,
                'rating': 4.4,
                'total_jobs': 30,
                'total_earnings': 45000.00,
                'service': created_services[3],
            }
        )

        self.stdout.write(self.style.SUCCESS("Vendor profiles created"))

        # --- 5. Professionals ---
        pro_data = [
            {'name': 'Rajesh Kumar', 'service': created_services[0], 'experience': 6, 'rating': 4.6, 'jobs_completed': 120},
            {'name': 'Suresh Yadav', 'service': created_services[1], 'experience': 4, 'rating': 4.3, 'jobs_completed': 85},
            {'name': 'Manish Gupta', 'service': created_services[2], 'experience': 8, 'rating': 4.8, 'jobs_completed': 200},
            {'name': 'Deepak Verma', 'service': created_services[3], 'experience': 3, 'rating': 4.2, 'jobs_completed': 60},
            {'name': 'Anita Devi', 'service': created_services[7], 'experience': 7, 'rating': 4.9, 'jobs_completed': 150},
        ]

        for pdata in pro_data:
            Professional.objects.get_or_create(
                name=pdata['name'],
                service=pdata['service'],
                defaults={
                    'experience': pdata['experience'],
                    'rating': pdata['rating'],
                    'jobs_completed': pdata['jobs_completed'],
                }
            )

        self.stdout.write(self.style.SUCCESS("Professionals created"))

        # --- 6. Bookings ---
        today = timezone.now().date()
        bookings_data = [
            {
                'user': user,
                'service': created_services[0],
                'vendor': v1,
                'booking_date': today + timedelta(days=2),
                'booking_time': '10:00:00',
                'address': '123 MG Road, New Delhi',
                'status': 'pending',
                'payment_status': 'unpaid',
            },
            {
                'user': user,
                'service': created_services[2],
                'vendor': v1,
                'booking_date': today + timedelta(days=5),
                'booking_time': '14:00:00',
                'address': '456 Connaught Place, New Delhi',
                'status': 'confirmed',
                'payment_status': 'paid',
            },
            {
                'user': user2,
                'service': created_services[3],
                'vendor': v2,
                'booking_date': today - timedelta(days=3),
                'booking_time': '11:00:00',
                'address': '789 Sector 18, Noida',
                'status': 'completed',
                'payment_status': 'paid',
            },
            {
                'user': user2,
                'service': created_services[4],
                'vendor': v2,
                'booking_date': today + timedelta(days=1),
                'booking_time': '09:00:00',
                'address': '321 DLF Phase 3, Gurugram',
                'status': 'pending',
                'payment_status': 'unpaid',
            },
            {
                'user': user,
                'service': created_services[6],
                'vendor': v1,
                'booking_date': today - timedelta(days=7),
                'booking_time': '16:00:00',
                'address': '555 Lajpat Nagar, New Delhi',
                'status': 'cancelled',
                'payment_status': 'unpaid',
            },
        ]

        created_bookings = []
        for bdata in bookings_data:
            b, created = Booking.objects.get_or_create(
                user=bdata['user'],
                service=bdata['service'],
                vendor=bdata['vendor'],
                booking_date=bdata['booking_date'],
                defaults={
                    'booking_time': bdata['booking_time'],
                    'address': bdata['address'],
                    'status': bdata['status'],
                    'payment_status': bdata['payment_status'],
                }
            )
            created_bookings.append(b)

        self.stdout.write(self.style.SUCCESS(f"{len(created_bookings)} Bookings created"))

        # --- 7. Payments ---
        for b in created_bookings:
            if b.payment_status == 'paid':
                Payment.objects.get_or_create(
                    booking=b,
                    defaults={
                        'amount': b.service.price,
                        'payment_status': 'completed',
                        'payment_method': 'razorpay',
                    }
                )

        self.stdout.write(self.style.SUCCESS("Payments created"))

        # --- 8. Reviews ---
        reviews_data = [
            {'user': user, 'service': created_services[0], 'rating': 5, 'comment': 'Absolutely amazing cleaning service! My house looks brand new. Highly recommended.'},
            {'user': user2, 'service': created_services[0], 'rating': 4, 'comment': 'Very good job, took a bit longer than expected. Overall happy.'},
            {'user': user, 'service': created_services[2], 'rating': 5, 'comment': 'Top-notch electrical work. Very professional and safety-conscious.'},
            {'user': user2, 'service': created_services[3], 'rating': 4, 'comment': 'AC is running like new after the service. Great value for money.'},
            {'user': user, 'service': created_services[4], 'rating': 5, 'comment': 'Beautiful painting work! The colors are vibrant and evenly applied.'},
            {'user': user2, 'service': created_services[7], 'rating': 5, 'comment': 'Stunning bridal makeup! Everyone complimented the look. Best in the city.'},
        ]

        for rdata in reviews_data:
            Review.objects.get_or_create(
                user=rdata['user'],
                service=rdata['service'],
                defaults={
                    'rating': rdata['rating'],
                    'comment': rdata['comment'],
                }
            )

        self.stdout.write(self.style.SUCCESS("Reviews created"))

        # --- 9. Favorites ---
        Favorite.objects.get_or_create(user=user, service=created_services[0])
        Favorite.objects.get_or_create(user=user, service=created_services[7])
        Favorite.objects.get_or_create(user=user2, service=created_services[2])

        self.stdout.write(self.style.SUCCESS("Favorites created"))

        self.stdout.write(self.style.SUCCESS("\nAll example data and images seeded successfully!\n"))
        self.stdout.write("Test accounts:")
        self.stdout.write("  user@test.com / testpassword123  (Customer)")
        self.stdout.write("  user2@test.com / testpassword123  (Customer)")
        self.stdout.write("  vendor@test.com / testpassword123  (Vendor)")
        self.stdout.write("  vendor2@test.com / testpassword123  (Vendor)")
        self.stdout.write("  admin@test.com / testpassword123  (Admin)")
