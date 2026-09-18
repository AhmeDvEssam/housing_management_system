import os, sys, django, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Allocation, AllocationType

print('=== Units with allocation field set ===')
units_with_alloc = Unit.objects.exclude(allocation__isnull=True).exclude(allocation='')
print(f'Count: {units_with_alloc.count()}')

print()
print('=== Allocation model records ===')
allocs = Allocation.objects.all().select_related('unit', 'unit__floor', 'unit__floor__building')
print(f'Count: {allocs.count()}')
for a in allocs:
    print(f'  ID={a.id} | Unit={a.unit.unit_no} ({a.unit.floor.building.name}) | Type={a.allocation_type} ({a.get_allocation_type_display()}) | To={a.allocated_to} | unit.allocation field="{a.unit.allocation}"')

print()
print('=== AllocationType choices ===')
print(AllocationType.choices)

print()
print('=== Bookings with ALLOCATIONS type ===')
from bookings.models import Booking, BookingType
alloc_bookings = Booking.objects.filter(booking_type=BookingType.ALLOCATIONS)
print(f'Count: {alloc_bookings.count()}')
for b in alloc_bookings[:5]:
    print(f'  Booking #{b.id}: Unit={b.unit}, Guest={b.guest_name}, Status={b.status}')
