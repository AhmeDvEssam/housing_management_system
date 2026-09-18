import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("""
    SELECT mc.MEM_NO, mc.MEMBER_CONTRACT_TYPE 
    FROM MEMBER_CONTRACT mc 
    WHERE mc.FLAT_ID = '666' 
    AND mc.START_FTRA_DATE = TO_DATE('2026-07-26', 'YYYY-MM-DD')
""")
print('Rows in DB for FLAT 666 on 26-JUL-2026:', cur.fetchall())

cur.close()
conn.close()
