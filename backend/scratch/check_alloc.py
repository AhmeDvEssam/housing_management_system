import os, sys, django, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking, BookingType

qs = Booking.objects.filter(booking_type=BookingType.ALLOCATIONS).values('guest_name', 'guest_id_no').distinct()[:10]
for r in qs:
    print(r)
