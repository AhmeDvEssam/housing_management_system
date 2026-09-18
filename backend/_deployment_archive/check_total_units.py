import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

import django
django.setup()

from inventory.models import Unit, Club
print(f"Total units in database: {Unit.objects.count()}")
