import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("""
    SELECT MEM_NO, MEMBER_CONTRACT_TYPE, START_FTRA_DATE 
    FROM MEMBER_CONTRACT 
    WHERE FLAT_ID = '657' 
    AND START_FTRA_DATE = TO_DATE('2026-08-03', 'YYYY-MM-DD')
""")
print('Occupants for FLAT 657 on 2026-08-03:', cur.fetchall())

cur.close()
conn.close()
