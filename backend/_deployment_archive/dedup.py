import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

def dedup():
    print("Deleting duplicates for ARMIES_REGIONS...")
    # Find duplicates
    # Since we synced twice, we can just delete all 2026 ARMIES_REGIONS bookings except the first 146! Or better, delete all ARMIES_REGIONS for 2026 and run the script one more time if needed.
    # Let's see how many there are.
    count = Booking.objects.filter(booking_type="ARMIES_REGIONS", start_date__year=2026).count()
    print("Total ARMIES_REGIONS:", count)
    
    # Let's delete ALL of them and resync just contracts? No, sync already finished, it created them.
    # Let's just group by guest_id_no, start_date, flat_id and keep the FIRST one.
    from django.db.models import Count
    
    deleted = 0
    duplicates = Booking.objects.filter(booking_type="ARMIES_REGIONS", start_date__year=2026).values('guest_id_no', 'start_date', 'unit').annotate(count=Count('id')).filter(count__gt=1)
    
    for dup in duplicates:
        # Keep the first, delete the rest
        bookings = list(Booking.objects.filter(
            booking_type="ARMIES_REGIONS",
            start_date__year=2026,
            guest_id_no=dup['guest_id_no'],
            start_date=dup['start_date'],
            unit=dup['unit']
        ).order_by('id'))
        
        for b in bookings[1:]:
            b.delete()
            deleted += 1
            
    print(f"Deleted {deleted} duplicates.")

dedup()
