import os
import django
import oracledb
from datetime import datetime
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

CLUB_MAP_FILE = os.path.join('scripts', 'club_map.json')
with open(CLUB_MAP_FILE, 'r', encoding='utf-8') as f:
    CLUB_MAP = json.load(f)

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

oracle_bookings = set()

# PERSON_BOOKED
cur.execute("SELECT pb.PERSON_NAME, f.PLA_CODE, f.FLAT_NUM, pb.BOOKED_START, pb.BOOKED_END FROM PERSON_BOOKED pb JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID WHERE EXTRACT(YEAR FROM pb.BOOKED_START) = 2025")
for row in cur.fetchall():
    name, club_id, flat_num, start, end = row
    if not start or not end: continue
    club_name = CLUB_MAP.get(str(club_id), str(club_id))
    oracle_bookings.add((str(club_name), str(flat_num), start.date(), end.date()))

# MEMBER_CONTRACT
cur.execute("SELECT mc.MEM_NO, f.PLA_CODE, f.FLAT_NUM, mc.START_FTRA_DATE, mc.END_FTRA_DATE FROM MEMBER_CONTRACT mc JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID WHERE EXTRACT(YEAR FROM mc.START_FTRA_DATE) = 2025")
for row in cur.fetchall():
    mem_no, club_id, flat_num, start, end = row
    if not start or not end: continue
    club_name = CLUB_MAP.get(str(club_id), str(club_id))
    oracle_bookings.add((str(club_name), str(flat_num), start.date(), end.date()))

# Django Bookings
django_bookings = set()
for b in Booking.objects.filter(start_date__year=2025):
    db_club = b.unit.floor.building.club.name if b.unit else None
    db_flat = b.unit.unit_no if b.unit else None
    django_bookings.add((str(db_club), str(db_flat), b.start_date, b.end_date))

missing = []
for ob in oracle_bookings:
    club_name, flat_num, start, end = ob
    found = False
    for db in django_bookings:
        db_club, db_flat, db_start, db_end = db
        if db_club == club_name and db_flat == flat_num and db_start == start and db_end == end:
            found = True
            break
    if not found:
        missing.append(ob)

print(f'Missing bookings count: {len(missing)}')
for m in missing:
    print(m)

