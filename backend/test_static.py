from django.test import Client
import traceback
c=Client()
try:
    r=c.get('/static/admin/js/booking_member_fetch.js')
    print('Status:', r.status_code)
    if r.status_code == 500:
        print(r.content.decode('utf-8', errors='replace')[:2000])
except Exception as e:
    traceback.print_exc()
