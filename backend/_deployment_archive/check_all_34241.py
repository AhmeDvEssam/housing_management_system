import os
import django
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
from bookings.models import Booking
for b in Booking.objects.filter(member__membership_no='34241', start_date__year=2025).order_by('start_date'):
    print(f'{b.start_date} to {b.end_date} | Mem: {b.member.membership_no if b.member else None} | Unit: {b.unit.unit_no}')
