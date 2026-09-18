import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("""
    SELECT MEM_NO, MEMBER_CONTRACT_TYPE, START_FTRA_DATE, FTRA_ID
    FROM MEMBER_CONTRACT 
    WHERE FLAT_ID = '657' 
    AND START_FIRST_FTRA_DATE = TO_DATE('2026-05-23', 'YYYY-MM-DD')
""")
print('Occupants for FLAT 657 on First FTRA 23-MAY-2026:', cur.fetchall())

cur.close()
conn.close()
