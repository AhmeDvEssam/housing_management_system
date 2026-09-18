import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("SELECT COLUMN_NAME FROM ALL_CONS_COLUMNS WHERE CONSTRAINT_NAME = 'MEMBER_CONTRACT_U01' ORDER BY POSITION")
print('MEMBER_CONTRACT_U01 columns:', [r[0] for r in cur.fetchall()])

cur.execute("SELECT CONSTRAINT_NAME, CONSTRAINT_TYPE, TABLE_NAME FROM ALL_CONSTRAINTS WHERE TABLE_NAME = 'MEMBER_CONTRACT'")
print('All constraints on MEMBER_CONTRACT:', cur.fetchall())

cur.close()
conn.close()
