import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("""
    SELECT c.CONSTRAINT_NAME, c.CONSTRAINT_TYPE, cc.COLUMN_NAME 
    FROM ALL_CONSTRAINTS c
    JOIN ALL_CONS_COLUMNS cc ON c.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
    WHERE c.TABLE_NAME = 'MEMBER_CONTRACT' AND c.OWNER = 'MIGRATION_TEMP'
    AND c.CONSTRAINT_TYPE IN ('P', 'U')
""")
print("Unique/Primary Constraints on MEMBER_CONTRACT:")
for r in cur.fetchall():
    print(r)

# Check PERSON_BOOKED as well
cur.execute("""
    SELECT c.CONSTRAINT_NAME, c.CONSTRAINT_TYPE, cc.COLUMN_NAME 
    FROM ALL_CONSTRAINTS c
    JOIN ALL_CONS_COLUMNS cc ON c.CONSTRAINT_NAME = cc.CONSTRAINT_NAME
    WHERE c.TABLE_NAME = 'PERSON_BOOKED' AND c.OWNER = 'MIGRATION_TEMP'
    AND c.CONSTRAINT_TYPE IN ('P', 'U')
""")
print("\nUnique/Primary Constraints on PERSON_BOOKED:")
for r in cur.fetchall():
    print(r)
    
cur.close()
conn.close()
