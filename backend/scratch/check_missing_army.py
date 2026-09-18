import sys, os, oracledb
sys.stdout.reconfigure(encoding='utf-8')

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
cur = conn.cursor()

missing_members = [75698, 48442, 91165, 83013, 101580, 82907, 79880, 85018, 49607, 37032, 85571, 79450]

club_ids = (4,5,6,7,8,9,10,11,12,19,20,21,22,23,24,25,26,27,28,29,30,31,32)

print("=== Checking if these 12 members have army contracts in Oracle MEMBER_CONTRACT ===\n")

for mem_no in missing_members:
    cur.execute(f"""
        SELECT mc.MEM_NO, mc.MEMBER_CONTRACT_TYPE, mc.START_FTRA_DATE, mc.END_FTRA_DATE, 
               f.PLA_CODE, f.FLAT_NUM, mc.FROM_DATE, mc.TO_DATE, mc.MEMBER_CONTRACT_FLAG
        FROM MEMBER_CONTRACT mc
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
        WHERE mc.MEM_NO = {mem_no}
        AND mc.MEMBER_CONTRACT_TYPE != 9
        AND f.PLA_CODE IN {club_ids}
        ORDER BY mc.START_FTRA_DATE DESC
    """)
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"FOUND: MEM_NO={r[0]}, TYPE={r[1]}, START_FTRA={r[2]}, END_FTRA={r[3]}, PLA={r[4]}, FLAT={r[5]}, FROM={r[6]}, TO={r[7]}, FLAG={r[8]}")
    else:
        # Check without club filter
        cur.execute(f"""
            SELECT mc.MEM_NO, mc.MEMBER_CONTRACT_TYPE, mc.START_FTRA_DATE, mc.END_FTRA_DATE, 
                   f.PLA_CODE, f.FLAT_NUM, mc.FROM_DATE, mc.TO_DATE
            FROM MEMBER_CONTRACT mc
            JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
            WHERE mc.MEM_NO = {mem_no}
            AND mc.MEMBER_CONTRACT_TYPE != 9
            ORDER BY mc.START_FTRA_DATE DESC
        """)
        rows2 = cur.fetchall()
        if rows2:
            for r in rows2:
                print(f"FOUND (OTHER CLUB): MEM_NO={r[0]}, TYPE={r[1]}, START_FTRA={r[2]}, END_FTRA={r[3]}, PLA={r[4]}, FLAT={r[5]}, FROM={r[6]}, TO={r[7]}")
        else:
            # Check if the member_contract record exists at all
            cur.execute(f"SELECT COUNT(*) FROM MEMBER_CONTRACT WHERE MEM_NO = {mem_no}")
            total = cur.fetchone()[0]
            
            # Check if they exist in MEMBER table at all
            cur.execute(f"SELECT COUNT(*) FROM MEMBER WHERE MEM_NO = {mem_no}")
            mem_exists = cur.fetchone()[0]
            
            print(f"NOT FOUND: MEM_NO={mem_no} - Total contracts: {total}, Member exists: {mem_exists}")

cur.close()
conn.close()
