import os
import django
import sys
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking
wrong_bookings = Booking.objects.filter(start_date='2026-05-23')
print(f"Found {wrong_bookings.count()} wrong bookings.")
wrong_bookings.delete()
print("Deleted wrong bookings.")

with open(r'D:\housing\backend\scripts\last_sync_date.txt', 'w') as f:
    f.write('2000-01-01 00:00:00')
print("Reset last_sync_date to allow full re-sync of missing records.")
