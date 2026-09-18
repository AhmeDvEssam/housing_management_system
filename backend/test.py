import os, sys, django
sys.path.insert(0, r'd:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from members.models import Member
user = User.objects.get(username='admin')
c = Client()
c.force_login(user)

# get a member
m = Member.objects.first()
if m:
    res = c.get(f'/admin/bookings/booking/get-member-details/?membership_no={m.id}')
    print("STATUS:", res.status_code)
    print("CONTENT:", res.content.decode('utf-8'))
else:
    print("NO MEMBER FOUND")
