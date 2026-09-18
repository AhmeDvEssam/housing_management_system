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
    
    print("--- CLUB Table Data (Detailed) ---")
    cursor.execute("SELECT CLUB_CODE, CLUB_NAME FROM CLUB")
    for row in cursor:
        print(f"CODE: {row[0]} | NAME: {row[1]}")
        
    conn.close()

if __name__ == "__main__":
    main()
