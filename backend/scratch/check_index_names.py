import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("""
    SELECT INDEX_NAME, COLUMN_NAME, COLUMN_POSITION 
    FROM ALL_IND_COLUMNS 
    WHERE TABLE_NAME = 'MEMBER_CONTRACT' 
    ORDER BY INDEX_NAME, COLUMN_POSITION
""")
print('All indexes on MEMBER_CONTRACT:')
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
