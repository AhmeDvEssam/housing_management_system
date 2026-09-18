import os
import django
import oracledb
from pprint import pprint
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()
conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()
cur.execute("SELECT mc.FROM_DATE, mc.START_FTRA_DATE, mc.START_FIRST_FTRA_DATE FROM MEMBER_CONTRACT mc WHERE mc.MEM_NO='34241' AND EXTRACT(YEAR FROM mc.START_FTRA_DATE)=2025")
pprint(cur.fetchall())
