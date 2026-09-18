import os
import django
import oracledb
from pprint import pprint
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()
cur.execute("SELECT pb.MEM_NO, pb.BOOKED_START, pb.BOOKED_END FROM PERSON_BOOKED pb JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID WHERE f.FLAT_NUM='924' AND EXTRACT(YEAR FROM pb.BOOKED_START)=2025")
pprint(cur.fetchall())
