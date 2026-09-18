import os, sys, django, oracledb

# Setup Django
sys.path.append(r"d:\housing\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

try:
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM MEMBER_CONTRACT WHERE TRUNC(RECORD_DATE) = TO_DATE('2026-07-01', 'YYYY-MM-DD')")
    mc_count_all = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM PERSON_BOOKED WHERE TRUNC(RECORD_DATE) = TO_DATE('2026-07-01', 'YYYY-MM-DD')")
    pb_count_all = cursor.fetchone()[0]
    
    print(f"Total MEMBER_CONTRACT across all clubs: {mc_count_all}")
    print(f"Total PERSON_BOOKED across all clubs: {pb_count_all}")
    print(f"Grand Total in Oracle: {mc_count_all + pb_count_all}")
    
except Exception as e:
    print(f"Error: {e}")
