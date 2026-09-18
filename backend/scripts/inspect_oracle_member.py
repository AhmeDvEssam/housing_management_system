import oracledb

def get_db_conn():
    return oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')

conn = get_db_conn()
if conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mc.FLAT_ID, f.FLAT_NUM, f.PLA_CODE, mc.FOR_YEAR, mc.FROM_DATE, mc.TO_DATE, mc.RECORD_DATE 
        FROM MEMBER_CONTRACT mc
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
        WHERE mc.MEM_NO = 20114
    """)
    print('Oracle contracts for 20114:')
    for r in cursor.fetchall():
        print(f"  - FLAT_ID: {r[0]} | Room: {r[1]} | Club ID: {r[2]} | Year: {r[3]} | From: {r[4]} | To: {r[5]} | RecDate: {r[6]}")
    conn.close()
