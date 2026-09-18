import django
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r"d:\housing\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

def main():
    # Let's inspect the occupant of room 602 in نادي بورسعيد during 2026-08-27 to 2026-09-03
    occupant = Booking.objects.filter(
        unit__floor__building__club__name="نادي بورسعيد",
        unit__unit_no="602",
        start_date__lte="2026-09-03",
        end_date__gte="2026-08-27"
    )
    print(f"Occupants found: {occupant.count()}")
    for b in occupant:
        mem_no = b.member.membership_no if b.member else b.guest_id_no
        print(f"  - Member: {mem_no} | Name: {b.guest_name} | Type: {b.booking_type} | Status: {b.status} | Dates: {b.start_date} to {b.end_date}")

if __name__ == "__main__":
    main()
