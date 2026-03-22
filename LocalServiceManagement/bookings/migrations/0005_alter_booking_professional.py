# Migration to make professional nullable on Booking
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_alter_booking_vendor'),
        ('professionals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='professional',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='professionals.professional',
            ),
        ),
    ]
