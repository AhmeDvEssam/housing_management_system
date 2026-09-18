import os
import sys
import django
from datetime import datetime, date

# Use dynamic path based on the script location so it works on any drive (e.g. F:\Housing_Transfer)
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, 'backend')
sys.path.append(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit
from bookings.models import Booking
from django.db import transaction

today = date.today()
extra_units = list(Unit.objects.exclude(updated_at__date=today))
real_units = list(Unit.objects.filter(updated_at__date=today))

deleted_count = 0
moved_bookings = 0

with transaction.atomic():
    for dup in extra_units:
        club_id = dup.floor.building.club.id
        unit_no = dup.unit_no
        
        # Find a matching real unit in the same club with the same unit_no
        matching_real = [r for r in real_units if r.floor.building.club.id == club_id and r.unit_no == unit_no]
        
        if matching_real:
            real = matching_real[0] 
            bookings = Booking.objects.filter(unit=dup)
            b_count = bookings.count()
            if b_count > 0:
                bookings.update(unit=real)
                moved_bookings += b_count
            
            dup.delete()
            deleted_count += 1
        else:
            bookings = Booking.objects.filter(unit=dup)
            b_count = bookings.count()
            if b_count > 0:
                moved_bookings += b_count 
            dup.delete()
            deleted_count += 1

print(f"Deleted {deleted_count} duplicate units.")
print(f"Successfully moved or cleared {moved_bookings} bookings.")
