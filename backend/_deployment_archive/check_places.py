import oracledb
conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()
cur.execute("SELECT table_name FROM user_tables WHERE table_name LIKE '%PLACE%'")
print("Tables with PLACE:", cur.fetchall())

try:
    cur.execute("SELECT * FROM PLACE")
    cols = [desc[0] for desc in cur.description]
    print("Columns in PLACE:", cols)
    rows = cur.fetchall()
    print("Rows in PLACE:")
    for row in rows:
        print(row)
except Exception as e:
    print(e)
    
conn.close()
