import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from bookings.models import Booking

try:
    with open('debug_out.txt', 'w', encoding='utf-8') as f:
        for b in Booking.objects.all():
            f.write(f"Booking: ID={b.id}, unit={b.unit.unit_no}, start={b.start_date}, end={b.end_date}\n")
            days = list(b.booking_days.order_by('day').values_list('day', flat=True))
            if days:
                f.write(f"  Days: {days[0]} ... {days[-1]} (Count: {len(days)})\n")
            else:
                f.write("  Days: None\n")
            f.write("-" * 40 + "\n")
    print("Done")
except Exception as e:
    print(f"Error: {e}")
