import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("SELECT table_name FROM all_tables WHERE owner='MIGRATION_TEMP'")
tables = [r[0] for r in cur.fetchall()]
found = False
for t in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t} WHERE MEM_NO = 101580")
        c = cur.fetchone()[0]
        if c > 0:
            print(f'Found in {t}: {c}')
            found = True
    except Exception:
        pass
if not found:
    print('Not found anywhere in MIGRATION_TEMP schema.')

cur.close()
conn.close()
