import urllib.request
import json
url = 'http://127.0.0.1:8000/api/dashboard/wallboard/?start_date=2026-05-23'
try:
    req = urllib.request.urlopen(url)
    data = json.loads(req.read())
    unit = next(u for u in data['units'] if u['unit_no'] == '214' and u['building'] == 'عمارة 2 | بحري - صف اول - مكيف')
    for st in unit['statuses']:
        print(f"{st['date']} : status={st['status']}, booking_id={st['booking_id']}")
except Exception as e:
    print('Error:', e)
