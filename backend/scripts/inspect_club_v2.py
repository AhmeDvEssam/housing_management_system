import oracledb
import os
import sys
import io

# Fix encoding for Arabic characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    print("--- CLUB Table Columns ---")
    cursor.execute("SELECT column_name FROM all_tab_columns WHERE table_name = 'CLUB'")
    columns = [row[0] for row in cursor.fetchall()]
    print(", ".join(columns))
    
    print("\n--- CLUB Table Data ---")
    # We want CLUB_ID, CLUB_NAME at least.
    cursor.execute("SELECT * FROM CLUB")
    cols = [d[0] for d in cursor.description]
    for row in cursor:
        d = dict(zip(cols, row))
        # Print selected fields to avoid mess
        print(f"ID: {d.get('CLUB_ID') or d.get('PLA_CODE')} | Name: {d.get('CLUB_NAME') or d.get('PLA_NAME')}")
        
    conn.close()

if __name__ == "__main__":
    main()
