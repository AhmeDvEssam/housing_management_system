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
        
        print("--- Listing all tables in MIGRATION_TEMP with row counts ---")
        cursor.execute("SELECT table_name FROM all_tables WHERE owner = 'MIGRATION_TEMP' ORDER BY table_name")
        tables = [row[0] for row in cursor.fetchall()]
        
        results = []
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                results.append((table, count))
            except Exception as e:
                results.append((table, f"Error: {e}"))
                
        print("\nTable List and Row Counts:")
        # Sort by count (integers first, then strings)
        def sort_key(x):
            val = x[1]
            if isinstance(val, int):
                return (0, -val)  # Sort descending by count
            return (1, str(val))
            
        for t, c in sorted(results, key=sort_key):
            print(f" - {t}: {c}")
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to Oracle: {e}")

if __name__ == "__main__":
    main()
