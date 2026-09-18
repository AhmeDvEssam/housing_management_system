import oracledb
import os

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    print("--- FLAT Table Columns ---")
    cursor.execute("SELECT column_name, data_type FROM all_tab_columns WHERE table_name = 'FLAT'")
    for row in cursor:
        print(row)
        
    print("\n--- FLAT Table Sample (10 rows) ---")
    cursor.execute("SELECT * FROM FLAT WHERE ROWNUM <= 10")
    cols = [d[0] for d in cursor.description]
    for row in cursor:
        print(dict(zip(cols, row)))
        
    print("\n--- Clubs in Oracle (PLA_CODE) ---")
    cursor.execute("SELECT DISTINCT PLA_CODE FROM FLAT")
    for row in cursor:
        print(row)
        
    conn.close()

if __name__ == "__main__":
    main()
