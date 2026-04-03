import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club, Building, Floor, Unit
from members.models import Member
from bookings.models import Booking
from payments.models import Contract

# Create hierarchy
club, _ = Club.objects.get_or_create(name="نادي الاختبار")
building, _ = Building.objects.get_or_create(club=club, name="مبنى أ")
floor, _ = Floor.objects.get_or_create(building=building, level_number=1, defaults={"label": "الدور الأول"})
unit, _ = Unit.objects.get_or_create(floor=floor, unit_no="101", defaults={"unit_type": "ROOM", "capacity": 2})

# Create Member
member, _ = Member.objects.get_or_create(membership_no="9999", defaults={"full_name": "عضو تجريبي", "phone": "01000000000"})

# Create Booking
start = date.today()
end = start + timedelta(days=3)
booking = Booking.objects.filter(member=member, unit=unit).first()
if not booking:
    booking = Booking.objects.create(member=member, unit=unit, start_date=start, end_date=end, status="CONFIRMED")
    print(f"Created Booking {booking.id}")

# Create Contract
contract, created = Contract.objects.get_or_create(booking=booking, defaults={"contract_no": "TEST-C-001"})
if created:
    print(f"Created Contract {contract.id}")
else:
    print(f"Contract {contract.id} already exists")
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Created superuser admin:admin123")
