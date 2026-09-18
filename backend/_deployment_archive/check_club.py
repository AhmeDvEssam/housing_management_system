import os
import django
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

b = Booking.objects.filter(member__membership_no='34241', start_date__year=2025).first()
print(f'Club name: {repr(b.unit.floor.building.club.name)}')

