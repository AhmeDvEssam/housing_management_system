import os
import django
import oracledb
from pprint import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("SELECT f.FLAT_ID, f.FLAT_NUM, f.PLA_CODE, mc.START_FTRA_DATE, mc.MEM_NO FROM MEMBER_CONTRACT mc JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID WHERE f.FLAT_NUM IN ('0', '1', '500') AND EXTRACT(YEAR FROM mc.START_FTRA_DATE) = 2025")
print('--- ?? ???? MEMBER_CONTRACT ---')
for r in cur.fetchall(): print(r)

cur.execute("SELECT f.FLAT_ID, f.FLAT_NUM, f.PLA_CODE, pb.BOOKED_START, pb.MEM_NO, pb.PERSON_NAME FROM PERSON_BOOKED pb JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID WHERE f.FLAT_NUM IN ('0', '1', '500') AND EXTRACT(YEAR FROM pb.BOOKED_START) = 2025")
print('--- ?? ???? PERSON_BOOKED ---')
for r in cur.fetchall(): print(r)

