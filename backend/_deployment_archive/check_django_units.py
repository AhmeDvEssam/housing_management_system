import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

import django
django.setup()

import oracledb
from inventory.models import Unit, Club

print("Checking units directly in Django DB")
units = Unit.objects.filter(unit_no__in=['709', '1', '0'])
print(f"Found {units.count()} units matching those numbers.")
for u in units:
    print(f"Unit: {u.unit_no}, Club: {u.floor.building.club.name}")
