import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("""
    SELECT mc.MEM_NO, mc.MEMBER_CONTRACT_TYPE, mc.LOT_TYPE_ID, mc.START_FIRST_FTRA_DATE, mc.FTRA_ID, mc.FLAT_ID, mc.START_FTRA_DATE
    FROM MEMBER_CONTRACT mc 
    WHERE mc.FLAT_ID = '666' 
    AND mc.FTRA_ID = 9
    AND EXTRACT(YEAR FROM mc.START_FIRST_FTRA_DATE) = 2026
""")
print('Rows in DB for FLAT 666 and FTRA 9 in 2026:')
for r in cur.fetchall():
    print(r)

cur.close()
conn.close()
