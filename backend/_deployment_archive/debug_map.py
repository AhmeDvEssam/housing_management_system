import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from dashboard.views import WallboardApiView
from collections import namedtuple

Request = namedtuple('Request', ['query_params', 'user'])
class DummyUser:
    is_authenticated = True
request = Request(query_params={'start_date': '2026-04-26'}, user=DummyUser())

view = WallboardApiView()
response = view.get(request)

# Manually recreate the steps to find out why day 6 is None
from dashboard.views import apply_unit_filters, compute_unit_status
from inventory.models import Unit
from bookings.models import BookingDay, Booking
from datetime import timedelta

start_date = date(2026, 4, 26)
end_date = start_date + timedelta(days=7)
units_qs = Unit.objects.all()
units_qs, _ = apply_unit_filters(units_qs, request)
units = list(units_qs)

booking_days = list(
    BookingDay.objects.filter(unit__in=units, day__gte=start_date, day__lt=end_date)
    .select_related("booking")
    .order_by("day")
)

bookings_map = {unit.id: {} for unit in units}
for booking_day in booking_days:
    bookings_map[booking_day.unit_id][booking_day.day] = booking_day.booking

dates = [start_date + timedelta(days=i) for i in range(7)]

unit_1485 = next((u for u in units if u.id == 1485), None)
if unit_1485:
    print(f"Dates:")
    for d in dates:
        print(f"  {d}: map_has={d in bookings_map[1485]}")
    
    print(f"BookingDays in list for unit 1485:")
    for bd in booking_days:
        if bd.unit_id == 1485:
            print(f"  day={bd.day}, booking_id={bd.booking_id}")
