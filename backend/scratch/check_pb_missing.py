import sys, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

missing_members = [75698, 48442, 91165, 83013, 101580, 82907, 79880, 85018, 49607, 37032, 85571, 79450]

print("=== Checking if these 12 members are in PERSON_BOOKED for 2026 ===")
for mem_no in missing_members:
    cur.execute(f"""
        SELECT pb.MEM_NO, pb.PERSON_NAME, pb.BOOKED_START, pb.BOOKED_END, f.PLA_CODE, f.FLAT_NUM
        FROM PERSON_BOOKED pb
        JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID
        WHERE pb.MEM_NO = {mem_no}
        AND EXTRACT(YEAR FROM pb.BOOKED_START) = 2026
    """)
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"FOUND in PERSON_BOOKED: MEM_NO={r[0]}, NAME={r[1]}, START={r[2]}, END={r[3]}, PLA={r[4]}, FLAT={r[5]}")
    else:
        print(f"NOT FOUND in PERSON_BOOKED for 2026: MEM_NO={mem_no}")

cur.close()
conn.close()
