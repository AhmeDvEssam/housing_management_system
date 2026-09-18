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
    
    print("--- Mapping Names in CONTWIN1 ---")
    cursor.execute("SELECT DISTINCT CLUB_NAME, PLA_NAME FROM CONTWIN1")
    for row in cursor:
        print(f"CLUB_NAME: {row[0]} | PLA_NAME: {row[1]}")
        
    conn.close()

if __name__ == "__main__":
    main()
