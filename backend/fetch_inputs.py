import os, sys, django
sys.path.insert(0, r"d:\housing\backend")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create superuser if not exists to ensure login works
try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    user = User.objects.create_superuser('admin', 'admin@example.com', '1')

c = Client()
c.force_login(user)

response = c.get('/admin/bookings/booking/add/')
html = response.content.decode('utf-8')

from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

print("=== SELECT / INPUT IDs ===")
for tag in soup.find_all(['select', 'input']):
    id_val = tag.get('id', '')
    if 'guest' in id_val or 'member' in id_val:
        print(f"[{tag.name}] id='{id_val}' name='{tag.get('name')}' class='{' '.join(tag.get('class', []))}'")

