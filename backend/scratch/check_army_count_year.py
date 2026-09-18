import os
import django
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

total_army = Booking.objects.filter(booking_type='ARMIES_REGIONS').count()
print(f"Total ARMY contracts: {total_army}")

from django.db.models import Count
qs = Booking.objects.filter(booking_type='ARMIES_REGIONS').values('start_date__year').annotate(c=Count('id'))
for row in qs:
    print(row)
