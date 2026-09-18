import os
import django
import oracledb
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()
cur.execute("SELECT mc.MEM_NO, f.FLAT_NUM, mc.START_FTRA_DATE, mc.END_FTRA_DATE FROM MEMBER_CONTRACT mc JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID WHERE EXTRACT(YEAR FROM mc.START_FTRA_DATE)=2025 AND f.FLAT_NUM='924'")
for r in cur.fetchall():
    print(r)
print('---')
cur.execute("SELECT pb.MEM_NO, f.FLAT_NUM, pb.BOOKED_START, pb.BOOKED_END FROM PERSON_BOOKED pb JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID WHERE EXTRACT(YEAR FROM pb.BOOKED_START)=2025 AND f.FLAT_NUM='924'")
for r in cur.fetchall():
    print(r)
