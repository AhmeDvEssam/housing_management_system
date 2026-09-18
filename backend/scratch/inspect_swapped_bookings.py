import django
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r"d:\housing\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking, BookingType

def main():
    swapped = Booking.objects.filter(notes__contains="تغيير الغرفة تلقائياً")
    print(f"Total swapped bookings: {swapped.count()}")
    
    for idx, b in enumerate(swapped[:15]):
        mem_no = b.member.membership_no if b.member else b.guest_id_no
        print(f"\n{idx+1}. Member No: {mem_no} | Name: {b.guest_name}")
        print(f"   Current Assigned Room in Django: {b.unit.unit_no} in {b.unit.floor.building.club.name}")
        print(f"   Dates: {b.start_date} to {b.end_date}")
        print(f"   Notes: {b.notes}")
        
        # Let's check if this member has another booking during this period!
        other_bookings = Booking.objects.filter(
            guest_id_no=mem_no,
            start_date__lte=b.end_date,
            end_date__gte=b.start_date
        ).exclude(id=b.id)
        
        print(f"   Other bookings for this member in Django: {other_bookings.count()}")
        for ob in other_bookings:
            print(f"     - Room: {ob.unit.unit_no} | Type: {ob.booking_type} | Status: {ob.status} | Dates: {ob.start_date} to {ob.end_date}")

if __name__ == "__main__":
    main()
