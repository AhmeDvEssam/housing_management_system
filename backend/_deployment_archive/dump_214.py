import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from bookings.models import Booking

with open('unit_214_bookings.txt', 'w', encoding='utf-8') as f:
    for b in Booking.objects.filter(unit__unit_no='214'):
        f.write(f'Booking {b.id}: start={b.start_date}, end={b.end_date}, status={b.status}, guest={b.guest_name}\n')
