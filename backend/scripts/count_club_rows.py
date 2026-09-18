import oracledb
import os

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM CLUB")
    print(f"Total rows in CLUB: {cursor.fetchone()[0]}")
    conn.close()

if __name__ == "__main__":
    main()
