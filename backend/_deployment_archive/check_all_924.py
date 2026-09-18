import os
import django
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

for b in Booking.objects.filter(unit__unit_no='924', unit__floor__building__club__name='???? ??? ????').order_by('start_date'):
    print(f'Member: {b.member.membership_no if b.member else None}, Start: {b.start_date}, End: {b.end_date}')
