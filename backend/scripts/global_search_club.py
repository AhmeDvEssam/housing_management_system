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
    
    # Search for a known club name in all character columns of all tables
    search_term = 'نادى 6 اكتوبر بورسعيد'
    
    print(f"--- Searching for '{search_term}' in all tables ---")
    cursor.execute("SELECT table_name, column_name FROM all_tab_columns WHERE owner = 'MIGRATION_TEMP' AND data_type LIKE '%CHAR%'")
    columns = cursor.fetchall()
    
    for table, column in columns:
        try:
            # We use a simple query to see if the value exists
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} LIKE :val", val=f"%{search_term}%")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"Found in Table: {table}, Column: {column} (Count: {count})")
        except:
            pass
            
    conn.close()

if __name__ == "__main__":
    main()
