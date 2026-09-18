import os
import sys
import io
import oracledb
import django
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

def check_one():
    django_qs = Booking.objects.filter(record_date__year=2025, status='مؤكد').select_related('unit__floor__building__club')
    if django_qs.exists():
        b = django_qs.first()
        print(f"Django: mem={b.guest_id_no}, club={b.unit.floor.building.club.id}, flat={b.unit.unit_no}, start={b.start_date}, end={b.end_date}")
        
    conn = oracledb.connect(user="migration_temp", password="migration", dsn="localhost/xe")
    cursor = conn.cursor()
    cursor.execute("SELECT mc.MEM_NO, f.PLA_CODE, f.FLAT_NUM, mc.FROM_DATE, mc.TO_DATE FROM MEMBER_CONTRACT mc JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID WHERE EXTRACT(YEAR FROM mc.RECORD_DATE) = 2025 AND mc.MEMBER_CONTRACT_FLAG = 1 FETCH FIRST 1 ROWS ONLY")
    r = cursor.fetchone()
    print(f"Oracle: mem={r[0]}, club={r[1]}, flat={r[2]}, start={r[3].date() if r[3] else None}, end={r[4].date() if r[4] else None}")
    
check_one()
