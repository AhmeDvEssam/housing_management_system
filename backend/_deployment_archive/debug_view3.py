import os
import django
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from dashboard.views import WallboardApiView, compute_unit_status
from inventory.models import Unit
from bookings.models import BookingDay

start_date = date(2026, 4, 26)
end_date = start_date + timedelta(days=7)

units = list(Unit.objects.filter(unit_no="214"))
if not units:
    print("Unit 214 not found")
else:
    unit = units[0]
    booking_days = BookingDay.objects.filter(unit=unit, day__gte=start_date, day__lt=end_date).select_related("booking")
    
    bookings_map = {}
    for bd in booking_days:
        bookings_map[bd.day] = bd.booking
        
    dates = [start_date + timedelta(days=i) for i in range(7)]
    for day in dates:
        booking = bookings_map.get(day)
        print(f"Day {day}: booking={'YES' if booking else 'NO'}")
