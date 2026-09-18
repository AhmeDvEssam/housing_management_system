import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from members.models import Member, FamilyMember
from bookings.models import Booking, Companion
from inventory.models import Unit, Club

print(f"Clubs: {Club.objects.count()}")
print(f"Units: {Unit.objects.count()}")
print(f"Members: {Member.objects.count()}")
print(f"Family Members: {FamilyMember.objects.count()}")
print(f"Bookings: {Booking.objects.count()}")
print(f"Companions: {Companion.objects.count()}")
