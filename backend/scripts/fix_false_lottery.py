"""
Fix script: Reset the 172 bookings incorrectly tagged as LOTTERY back to STANDARD.
These bookings were marked as lottery because the old smart_sync matched
membership_no + unit_no without checking the club name, causing false positives.
"""
import sys, io, os, django
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking, BookingType, BookingDay
from django.db import transaction

print("=== Fixing incorrectly tagged lottery bookings ===")

lottery_bookings = Booking.objects.filter(booking_type=BookingType.LOTTERY)
count = lottery_bookings.count()
print(f"Found {count} bookings tagged as LOTTERY")

if count > 0:
    # These are all false positives from the DMP import
    # They should be STANDARD + confirmed
    updated = 0
    for b in lottery_bookings:
        b.booking_type = BookingType.STANDARD
        b.status = "مؤكد"
        # Use super().save() to avoid full_clean validation overhead
        Booking.objects.filter(pk=b.pk).update(
            booking_type=BookingType.STANDARD,
            status="مؤكد"
        )
        updated += 1
    
    print(f"[SUCCESS] Fixed {updated} bookings: LOTTERY -> STANDARD, غير مؤكد -> مؤكد")
    
    # Verify
    remaining = Booking.objects.filter(booking_type=BookingType.LOTTERY).count()
    unconfirmed = Booking.objects.filter(status="غير مؤكد").count()
    print(f"\nVerification:")
    print(f"  Remaining lottery bookings: {remaining}")
    print(f"  Remaining unconfirmed bookings: {unconfirmed}")
else:
    print("No lottery bookings to fix.")
