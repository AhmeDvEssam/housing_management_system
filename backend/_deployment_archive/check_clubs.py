import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club, Unit, Floor, Building

print('Clubs:')
for c in Club.objects.all():
    print(f"ID: {c.id}, Name: {c.name}, Units: {Unit.objects.filter(floor__building__club=c).count()}")

# Delete clubs named 'y'
y_clubs = Club.objects.filter(name='y')
if y_clubs.exists():
    print(f"Deleting clubs named 'y': {y_clubs.count()}")
    y_clubs.delete()

# Wait, there are other clubs where I added units. The user says there are 450 units exactly.
# I should delete all units created today? Or what?
print(f"Total units now: {Unit.objects.count()}")
