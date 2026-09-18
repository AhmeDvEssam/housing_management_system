import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club, Unit

with open('clubs_info.txt', 'w', encoding='utf-8') as f:
    f.write('Clubs:\n')
    for c in Club.objects.all():
        units_count = Unit.objects.filter(floor__building__club=c).count()
        f.write(f"ID: {c.id}, Name: {c.name}, Units: {units_count}\n")
