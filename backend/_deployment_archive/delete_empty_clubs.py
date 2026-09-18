import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club, Unit

empty_clubs = []
for c in Club.objects.all():
    units_count = Unit.objects.filter(floor__building__club=c).count()
    if units_count == 0:
        empty_clubs.append(c)

print(f"Deleting {len(empty_clubs)} clubs that have 0 units...")
for c in empty_clubs:
    print(f"Deleting club: {c.name}")
    c.delete()
