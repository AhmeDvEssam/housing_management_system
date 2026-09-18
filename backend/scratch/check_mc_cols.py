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
print(f"{'#':>3s} {'COLUMN_NAME':35s} {'DATA_TYPE':15s} {'BYTES':>8s} {'CHARS':>8s}")
print("-" * 75)
for i, r in enumerate(cur.fetchall(), 1):
    print(f"{i:>3d} {r[0]:35s} {r[1]:15s} {r[2]:>8d} {r[3]:>8}")

# Also check max actual data lengths for text columns
print("\n\n=== Actual max data lengths for VARCHAR2 columns ===\n")
cur.execute("""
    SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS 
    WHERE TABLE_NAME = 'MEMBER_CONTRACT' AND DATA_TYPE = 'VARCHAR2'
    ORDER BY COLUMN_ID
""")
varchar_cols = [r[0] for r in cur.fetchall()]

for col in varchar_cols:
    try:
        cur.execute(f"SELECT MAX(LENGTH({col})) FROM MEMBER_CONTRACT")
        max_len = cur.fetchone()[0]
        cur.execute(f"SELECT CHAR_LENGTH FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = 'MEMBER_CONTRACT' AND COLUMN_NAME = '{col}'")
        col_limit = cur.fetchone()[0]
        pct = (max_len / col_limit * 100) if max_len and col_limit else 0
        flag = " *** NEAR LIMIT!" if pct > 90 else ""
        print(f"  {col:35s} max_actual={max_len:>6} / limit={col_limit:>6}  ({pct:.0f}%){flag}")
    except Exception as e:
        print(f"  {col:35s} ERROR: {e}")

cur.close()
conn.close()
