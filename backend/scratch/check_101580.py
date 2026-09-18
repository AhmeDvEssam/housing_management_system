import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("SELECT * FROM MEMBER_CONTRACT WHERE MEM_NO = 101580")
print('Contracts for 101580:', len(cur.fetchall()))

cur.execute("SELECT * FROM PERSON_BOOKED WHERE MEM_NO = 101580")
print('Person booked for 101580:', len(cur.fetchall()))

cur.close()
conn.close()
