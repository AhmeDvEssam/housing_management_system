import os, sys, django, oracledb

sys.path.append(r"d:\housing\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

try:
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    cursor.execute("SELECT column_name FROM user_tab_columns WHERE table_name = 'MEMBER_CONTRACT'")
    print("MEMBER_CONTRACT columns:")
    print([r[0] for r in cursor.fetchall()])
    
    cursor.execute("SELECT column_name FROM user_tab_columns WHERE table_name = 'PERSON_BOOKED'")
    print("PERSON_BOOKED columns:")
    print([r[0] for r in cursor.fetchall()])
except Exception as e:
    print(f"Error: {e}")
