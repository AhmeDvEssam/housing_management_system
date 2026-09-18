import oracledb
import os

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    print("--- Searching for tables with PLA_CODE or CLUB_CODE ---")
    cursor.execute("SELECT table_name, column_name FROM all_tab_columns WHERE owner = 'MIGRATION_TEMP' AND (column_name = 'PLA_CODE' OR column_name = 'CLUB_CODE' OR column_name = 'CLUB_ID')")
    for row in cursor:
        print(row)
        
    conn.close()

if __name__ == "__main__":
    main()
