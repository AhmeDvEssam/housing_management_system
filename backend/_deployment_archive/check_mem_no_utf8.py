import os
import django
import oracledb
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()
cur.execute("SELECT f.FLAT_NUM, pb.BOOKED_START, pb.MEM_NO, pb.PERSON_NAME FROM PERSON_BOOKED pb JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID WHERE f.FLAT_NUM IN ('0', '1', '500') AND EXTRACT(YEAR FROM pb.BOOKED_START) = 2025")
for r in cur.fetchall(): print(r)
