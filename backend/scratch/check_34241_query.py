import os, sys, django, io, oracledb
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = oracledb.connect(user='migration_temp', password='migration', dsn='localhost/xe')
cursor = conn.cursor()
query = "SELECT mc.MEM_NO, f.PLA_CODE, f.FLAT_NUM, mc.START_FTRA_DATE, mc.END_FTRA_DATE, 'MEMBER_CONTRACT' as SRC FROM MEMBER_CONTRACT mc JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID WHERE EXTRACT(YEAR FROM mc.RECORD_DATE) = 2025 AND mc.MEMBER_CONTRACT_FLAG = 1 AND f.FLAT_NUM='924'"
cursor.execute(query)
rows = cursor.fetchall()
print([row for row in rows if row[0] == 34241])
