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
    
    print("--- Distinct Club Names and Codes in CONTWIN1 ---")
    try:
        # Let's see all columns first to be sure
        cursor.execute("SELECT * FROM CONTWIN1 WHERE ROWNUM = 1")
        cols = [d[0] for d in cursor.description]
        print(f"Columns: {cols}")
        
        # Try to find name and code
        name_col = 'CLUB_NAME'
        code_col = 'PLA_CODE' if 'PLA_CODE' in cols else ('CLUB_CODE' if 'CLUB_CODE' in cols else 'CLUB_ID')
        
        cursor.execute(f"SELECT DISTINCT {code_col}, {name_col} FROM CONTWIN1")
        for row in cursor:
            print(f"CODE: {row[0]} | NAME: {row[1]}")
    except Exception as e:
        print(f"Error: {e}")
        
    conn.close()

if __name__ == "__main__":
    main()
