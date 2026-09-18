import os
import django
import json
from collections import namedtuple

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from dashboard.views import WallboardApiView

Request = namedtuple('Request', ['query_params', 'user'])
class DummyUser:
    is_authenticated = True
request = Request(query_params={'start_date': '2026-04-26'}, user=DummyUser())

view = WallboardApiView()
response = view.get(request)

with open('api_response.json', 'w', encoding='utf-8') as f:
    json.dump(response.data, f, ensure_ascii=False, indent=2)

print("Done")
