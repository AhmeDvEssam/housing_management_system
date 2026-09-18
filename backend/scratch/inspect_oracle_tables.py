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
        
        tables = ['WIN_TEMP', 'MEMBER_ESTMARA', 'LOT_EXCLUDE', 'FTRA_LOT']
        
        for table in tables:
            print(f"\n========================================\nTable: {table}")
            try:
                # Get column info
                cursor.execute(f"SELECT column_name, data_type FROM all_tab_columns WHERE owner = 'MIGRATION_TEMP' AND table_name = '{table}'")
                cols = cursor.fetchall()
                print("Columns:")
                for col in cols:
                    print(f"  - {col[0]} ({col[1]})")
                
                # Fetch 3 sample rows
                cursor.execute(f"SELECT * FROM {table} WHERE ROWNUM <= 3")
                rows = cursor.fetchall()
                print("\nSamples:")
                for row in rows:
                    print(f"  {row}")
            except Exception as e:
                print(f"Error inspecting {table}: {e}")
                
        conn.close()
    except Exception as e:
        print(f"Error connecting to Oracle: {e}")

if __name__ == "__main__":
    main()
