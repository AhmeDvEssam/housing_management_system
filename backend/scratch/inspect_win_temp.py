import oracledb
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
        cursor = conn.cursor()
        
        print("--- Inspecting unique values in WIN_TEMP ---")
        
        cursor.execute("SELECT COUNT(*) FROM WIN_TEMP")
        print(f"Total count in WIN_TEMP: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT START_FIRST_FTRA_DATE, COUNT(*) FROM WIN_TEMP GROUP BY START_FIRST_FTRA_DATE")
        print("\nBy START_FIRST_FTRA_DATE:")
        for row in cursor.fetchall():
            print(f"  - Date: {row[0]} | Count: {row[1]}")
            
        cursor.execute("SELECT LOT_TYPE_ID, COUNT(*) FROM WIN_TEMP GROUP BY LOT_TYPE_ID")
        print("\nBy LOT_TYPE_ID:")
        for row in cursor.fetchall():
            print(f"  - Lot Type ID: {row[0]} | Count: {row[1]}")
            
        cursor.execute("SELECT LAST_LOT, COUNT(*) FROM WIN_TEMP GROUP BY LAST_LOT")
        print("\nBy LAST_LOT:")
        for row in cursor.fetchall():
            print(f"  - Last Lot: {row[0]} | Count: {row[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to Oracle: {e}")

if __name__ == "__main__":
    main()
