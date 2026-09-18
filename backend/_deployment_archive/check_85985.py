import os
import django
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

b = Booking.objects.filter(member__membership_no='85985', start_date__year=2025).first()
if b:
    print(f'Start: {b.start_date}, Unit: {b.unit.unit_no}')
else:
    print('No booking found for 85985 in 2025')
