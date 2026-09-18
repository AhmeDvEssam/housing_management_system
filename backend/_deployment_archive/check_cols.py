import os, sys, oracledb
ORACLE_USER = 'MIGRATION_TEMP'
ORACLE_PASS = 'migration'
ORACLE_DSN = 'localhost:1521/xe'
try:
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM user_tab_columns WHERE table_name = 'PERSON_BOOKED'")
    cols = [r[0] for r in cur.fetchall()]
    print('Columns in PERSON_BOOKED:', cols)
    conn.close()
except Exception as e:
    print('Error:', e)
