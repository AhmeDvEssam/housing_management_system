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
total_contracts = Booking.objects.exclude(booking_type='ALLOCATIONS').filter(contract_detail__isnull=False).count()

print(f"Total synced contracts: {total_contracts}")
print(f"Total ARMY contracts: {total_army}")
