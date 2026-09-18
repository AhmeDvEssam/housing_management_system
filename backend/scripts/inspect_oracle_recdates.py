import oracledb

def get_db_conn():
    return oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')

conn = get_db_conn()
if conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TO_CHAR(RECORD_DATE, 'YYYY-MM-DD HH24:MI:SS'), COUNT(1) 
        FROM MEMBER_CONTRACT 
        WHERE FOR_YEAR = 2026 
        GROUP BY TO_CHAR(RECORD_DATE, 'YYYY-MM-DD HH24:MI:SS')
        ORDER BY COUNT(1) DESC
    """)
    print('Oracle RECORD_DATE distribution for 2026:')
    for r in cursor.fetchall()[:20]:
        print(f"  - Date: {r[0]} | Count: {r[1]}")
    conn.close()
