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
    
    print("--- Inspecting BUILDING Table ---")
    try:
        cursor.execute("SELECT * FROM BUILDING")
        cols = [d[0] for d in cursor.description]
        for row in cursor:
            print(dict(zip(cols, row)))
    except Exception as e: print(e)
    
    print("\n--- Inspecting FORMS_REPORTS Table ---")
    try:
        cursor.execute("SELECT * FROM FORMS_REPORTS")
        cols = [d[0] for d in cursor.description]
        for row in cursor:
            print(dict(zip(cols, row)))
    except Exception as e: print(e)
        
    conn.close()

if __name__ == "__main__":
    main()
