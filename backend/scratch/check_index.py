import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("SELECT COLUMN_NAME FROM ALL_IND_COLUMNS WHERE INDEX_NAME = 'MEMBER_CONTRACT_U01' ORDER BY COLUMN_POSITION")
print('Index columns for U01:', [r[0] for r in cur.fetchall()])

cur.execute("SELECT COLUMN_NAME FROM ALL_IND_COLUMNS WHERE TABLE_NAME = 'MEMBER_CONTRACT' ORDER BY INDEX_NAME, COLUMN_POSITION")
print('All indexes on MEMBER_CONTRACT:', [r[0] for r in cur.fetchall()])

cur.close()
conn.close()
