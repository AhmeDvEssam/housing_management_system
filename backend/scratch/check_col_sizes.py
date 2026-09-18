import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

cur.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, CHAR_LENGTH 
    FROM ALL_TAB_COLUMNS 
    WHERE TABLE_NAME = 'MEMBER_CONTRACT' 
    ORDER BY COLUMN_ID
""")

print("=== MEMBER_CONTRACT Column Definitions ===\n")
print(f"{'COLUMN_NAME':35s} {'DATA_TYPE':15s} {'BYTES':>8s} {'CHARS':>8s}")
print("-" * 70)
for r in cur.fetchall():
    print(f"{r[0]:35s} {r[1]:15s} {r[2]:>8d} {r[3]:>8}")

# Also check MEMBER table
print("\n\n=== MEMBER Column Definitions ===\n")
cur.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, CHAR_LENGTH 
    FROM ALL_TAB_COLUMNS 
    WHERE TABLE_NAME = 'MEMBER' 
    ORDER BY COLUMN_ID
""")
print(f"{'COLUMN_NAME':35s} {'DATA_TYPE':15s} {'BYTES':>8s} {'CHARS':>8s}")
print("-" * 70)
for r in cur.fetchall():
    print(f"{r[0]:35s} {r[1]:15s} {r[2]:>8d} {r[3]:>8}")

# Check PERSON_BOOKED too
print("\n\n=== PERSON_BOOKED Column Definitions ===\n")
cur.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH, CHAR_LENGTH 
    FROM ALL_TAB_COLUMNS 
    WHERE TABLE_NAME = 'PERSON_BOOKED' 
    ORDER BY COLUMN_ID
""")
print(f"{'COLUMN_NAME':35s} {'DATA_TYPE':15s} {'BYTES':>8s} {'CHARS':>8s}")
print("-" * 70)
for r in cur.fetchall():
    print(f"{r[0]:35s} {r[1]:15s} {r[2]:>8d} {r[3]:>8}")

cur.close()
conn.close()
