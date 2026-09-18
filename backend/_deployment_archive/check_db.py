import os, sys, django
sys.path.append('d:\\housing\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
from bookings.models import Unit, Booking
print(f'Total Units: {Unit.objects.count()}')
print(f'Total Bookings: {Booking.objects.count()}')
print(f'Total Allocations: {Booking.objects.filter(booking_type="ALLOCATIONS").count()}')
