import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from bookings.models import Booking

count = 0
for b in Booking.objects.all():
    b._set_booking_days()
    count += 1
print(f"Updated {count} bookings")
