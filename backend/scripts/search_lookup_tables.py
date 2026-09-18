import oracledb
import os

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    print("--- Searching for potential Club Lookup tables ---")
    cursor.execute("SELECT table_name, num_rows FROM all_tables WHERE owner = 'MIGRATION_TEMP' AND num_rows BETWEEN 20 AND 100")
    for row in cursor:
        print(row)
        
    conn.close()

if __name__ == "__main__":
    main()
