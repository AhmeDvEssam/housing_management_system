import os
import django
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

total_army = Booking.objects.exclude(booking_type='ALLOCATIONS').filter(contract_detail__isnull=False).exclude(contract_detail__contract_type=9).count()
total_contracts = Booking.objects.exclude(booking_type='ALLOCATIONS').filter(contract_detail__isnull=False).count()

print(f"Total synced contracts: {total_contracts}")
print(f"Total ARMY contracts (contract_type != 9): {total_army}")
