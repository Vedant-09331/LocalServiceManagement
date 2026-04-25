# Migration 0004 is now redundant as 0003 already adds vendor as nullable.
# This file is kept for migration history integrity but does nothing.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_booking_vendor'),
        ('vendors', '0001_initial'),
    ]

    operations = []
