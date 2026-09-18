import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("SELECT START_FTRA_DATE, FLAT_ID, MEMBER_CONTRACT_TYPE FROM MEMBER_CONTRACT WHERE MEM_NO = 79450")
rows = cur.fetchall()
print('Contracts for 79450 in Oracle:', rows)

cur.close()
conn.close()
