import oracledb
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    print("--- ESKAN_CLUBS_TAMAM Table Data ---")
    cursor.execute("SELECT column_name FROM all_tab_columns WHERE table_name = 'ESKAN_CLUBS_TAMAM'")
    cols = [r[0] for r in cursor.fetchall()]
    print(", ".join(cols))
    
    cursor.execute("SELECT * FROM ESKAN_CLUBS_TAMAM")
    for row in cursor:
        print(row)
        
    conn.close()

if __name__ == "__main__":
    main()
