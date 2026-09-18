import os
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from dashboard.views import WallboardApiView
from inventory.models import Unit
from bookings.models import BookingDay

start_date = date(2026, 5, 23)
end_date = date(2026, 5, 30)

days = BookingDay.objects.filter(unit_id=214, day__gte=start_date, day__lt=end_date).order_by('day')
print("DB BookingDays for Unit 214:")
for d in days:
    print(f"  {d.day} - Booking {d.booking.id}")

