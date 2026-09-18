import os, sys, django, oracledb

sys.path.append(r"d:\housing\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

try:
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    # 1. Count total where they are different
    cursor.execute("""
        SELECT COUNT(*) FROM MEMBER_CONTRACT 
        WHERE MEMBER_CONTRACT_DATE2 IS NOT NULL 
        AND TRUNC(RECORD_DATE) != TRUNC(MEMBER_CONTRACT_DATE2)
    """)
    diff_count = cursor.fetchone()[0]
    
    # 2. Count total where they are same
    cursor.execute("""
        SELECT COUNT(*) FROM MEMBER_CONTRACT 
        WHERE MEMBER_CONTRACT_DATE2 IS NOT NULL 
        AND TRUNC(RECORD_DATE) = TRUNC(MEMBER_CONTRACT_DATE2)
    """)
    same_count = cursor.fetchone()[0]
    
    print(f"Contracts with DIFFERENT Record Date & Contract Date: {diff_count}")
    print(f"Contracts with SAME Record Date & Contract Date: {same_count}")
    
except Exception as e:
    print(f"Error: {e}")
