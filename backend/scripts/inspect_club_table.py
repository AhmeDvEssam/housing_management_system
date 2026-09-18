import oracledb
import os

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    print("--- Inspecting CLUB Table ---")
    cursor.execute("SELECT column_name FROM all_tab_columns WHERE table_name = 'CLUB'")
    for row in cursor:
        print(row)
        
    print("\n--- CLUB Table Data ---")
    cursor.execute("SELECT * FROM CLUB")
    cols = [d[0] for d in cursor.description]
    for row in cursor:
        print(dict(zip(cols, row)))
        
    conn.close()

if __name__ == "__main__":
    main()
