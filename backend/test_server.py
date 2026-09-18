import urllib.request, traceback
try:
  r=urllib.request.urlopen('http://127.0.0.1:8080/static/admin/js/booking_member_fetch.js')
  print(r.getcode())
except urllib.error.HTTPError as e:
  print('ERROR:', e.code)
  print(e.read().decode('utf-8', errors='replace')[:2000])
except Exception as e:
  traceback.print_exc()
