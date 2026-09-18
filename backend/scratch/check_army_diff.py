import sys, os, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

club_ids = (4,5,6,7,8,9,10,11,12,19,20,21,22,23,24,25,26,27,28,29,30,31,32)

# Total army contracts for 2026
cur.execute(f"""
    SELECT COUNT(*)
    FROM MEMBER_CONTRACT mc
    JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
    WHERE mc.MEMBER_CONTRACT_TYPE != 9
    AND f.PLA_CODE IN {club_ids}
    AND EXTRACT(YEAR FROM mc.START_FTRA_DATE) = 2026
""")
print('Oracle army 2026:', cur.fetchone()[0])

# Get member numbers from Oracle
cur.execute(f"""
    SELECT mc.MEM_NO, mc.MEMBER_CONTRACT_TYPE, f.PLA_CODE, f.FLAT_NUM, mc.START_FTRA_DATE, mc.END_FTRA_DATE
    FROM MEMBER_CONTRACT mc
    JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
    WHERE mc.MEMBER_CONTRACT_TYPE != 9
    AND f.PLA_CODE IN {club_ids}
    AND EXTRACT(YEAR FROM mc.START_FTRA_DATE) = 2026
    ORDER BY mc.MEM_NO
""")
oracle_rows = cur.fetchall()
print(f"Oracle army 2026 detail: {len(oracle_rows)} rows")

# Now check Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
django.setup()
from bookings.models import Booking, BookingType

django_army = list(Booking.objects.filter(
    booking_type=BookingType.ARMIES_REGIONS,
    start_date__year=2026
).values_list('member__membership_no', 'start_date', 'end_date', 'unit__unit_no'))

django_mem_set = set()
for b in django_army:
    django_mem_set.add(str(b[0]))

print(f"\nDjango army 2026: {len(django_army)}")

# Find missing from Django
missing = []
for row in oracle_rows:
    mem_no = str(row[0])
    if mem_no not in django_mem_set:
        missing.append(row)

print(f"\nMissing from Django (in Oracle but not in Django): {len(missing)}")
for m in missing:
    mem_no, ct, pla, flat, start, end = m
    print(f"  MEM_NO={mem_no}, TYPE={ct}, CLUB={pla}, FLAT={flat}, START={start}, END={end}")

# Check why - member exists?
from members.models import Member
for m in missing:
    mem_no = str(m[0])
    mem = Member.objects.filter(membership_no=mem_no).first()
    if not mem:
        print(f"  -> MEM_NO {mem_no}: MEMBER NOT FOUND IN DJANGO!")
    else:
        print(f"  -> MEM_NO {mem_no}: Member exists ({mem.full_name})")

cur.close()
conn.close()
