import os
import django
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from dashboard.views import WallboardApiView, compute_unit_status
from inventory.models import Unit
from bookings.models import BookingDay

start_date = date(2026, 5, 23)
end_date = start_date + timedelta(days=7)

units = list(Unit.objects.filter(unit_no="214"))
unit = units[0]

booking_days = BookingDay.objects.filter(unit__in=units, day__gte=start_date, day__lt=end_date).select_related("booking")

bookings_map = {u.id: {} for u in units}
for bd in booking_days:
    bookings_map[bd.unit_id][bd.day] = bd.booking

dates = [start_date + timedelta(days=i) for i in range(7)]

print(f"Unit 214 ID is {unit.id}")
for day in dates:
    booking = bookings_map.get(unit.id, {}).get(day)
    status = compute_unit_status(unit, booking, day)
    print(f"Day {day}: booking={booking.id if booking else None}, status={status}")
