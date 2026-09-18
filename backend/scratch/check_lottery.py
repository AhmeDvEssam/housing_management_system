import os
import django
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking, BookingType
from django.db.models import Count

for row in Booking.objects.filter(booking_type=BookingType.LOTTERY).values('status').annotate(c=Count('id')):
    print(row)
