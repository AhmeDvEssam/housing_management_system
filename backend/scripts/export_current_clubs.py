import os
import django
import sys

# Setup Django
sys.path.append('d:\\housing\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club

with open('d:\\dmp\\scratch\\current_clubs_utf8.txt', 'w', encoding='utf-8') as f:
    for club in Club.objects.all():
        f.write(f"{club.id},{club.name}\n")
print("Done")
