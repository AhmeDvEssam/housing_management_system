
import os, django, re
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
c = Client()
c.force_login(User.objects.first())
html = c.get('/admin/reports/dailybookingreport/?from_date=2026-07-01').content.decode('utf-8')
with open('dump.html', 'w', encoding='utf-8') as f:
    f.write(html)

