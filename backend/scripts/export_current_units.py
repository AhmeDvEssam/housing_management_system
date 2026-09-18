import os
import django
import sys

# Setup Django
sys.path.append('d:\\housing\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit

with open('d:\\dmp\\scratch\\current_units_utf8.txt', 'w', encoding='utf-8') as f:
    for unit in Unit.objects.select_related('floor__building__club').all():
        f.write(f"{unit.id},{unit.floor.building.club.id},{unit.unit_no}\n")
print("Done")
