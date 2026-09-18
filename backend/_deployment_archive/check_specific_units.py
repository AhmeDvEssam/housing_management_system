import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

import django
django.setup()

import oracledb
from inventory.models import Unit, Club, Floor, Building

print("Checking Club 4 (فندق الانفوشي)")
club = Club.objects.filter(name="فندق الانفوشي").first()
if club:
    units = Unit.objects.filter(floor__building__club=club)
    print(f"Total units in {club.name}: {units.count()}")
    for u in units:
        print(f"  Unit: {u.unit_no}")
else:
    print("Club not found")
    
print("\\nChecking Club 5 (نادي بورسعيد)")
club2 = Club.objects.filter(name="نادي بورسعيد").first()
if club2:
    units = Unit.objects.filter(floor__building__club=club2)
    print(f"Total units in {club2.name}: {units.count()}")
    # Too many maybe, let's just check units with '0' or '1'
    for u in units.filter(unit_no__in=['0', '1']):
        print(f"  Unit: {u.unit_no}")
else:
    print("Club not found")
