import os
import django
import oracledb
from pprint import pprint
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()
cur.execute("SELECT mc.MEM_NO, mc.START_FTRA_DATE, mc.END_FTRA_DATE FROM MEMBER_CONTRACT mc JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID WHERE f.FLAT_NUM='924' AND EXTRACT(YEAR FROM mc.START_FTRA_DATE) = 2025 AND EXTRACT(MONTH FROM mc.START_FTRA_DATE) = 6")
pprint(cur.fetchall())
