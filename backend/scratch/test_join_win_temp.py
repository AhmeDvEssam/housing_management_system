import oracledb
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
        cursor = conn.cursor()
        
        print("--- Testing Join of WIN_TEMP, FLAT, and MEMBER for 2026 ---")
        query = """
            SELECT wt.MEM_NO, m.MEM_NAME, m.TELEPHONES, f.PLA_CODE, f.FLAT_NUM, wt.FTRA_ID, f.SLLEEP_ROOM, f.BED_NUM
            FROM WIN_TEMP wt
            LEFT JOIN FLAT f ON wt.FLAT_ID = CAST(f.FLAT_ID AS VARCHAR2(50))
            LEFT JOIN MEMBER m ON wt.MEM_NO = m.MEM_NO
            WHERE wt.START_FIRST_FTRA_DATE = TO_DATE('2026-05-23', 'YYYY-MM-DD')
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"Total joined rows for 2026: {len(rows)}")
        
        print("\nFirst 10 joined samples with Member details:")
        for idx, row in enumerate(rows[:10]):
            mem_no, mem_name, phones, pla_code, flat_num, ftra_id, sleep_room, bed_num = row
            print(f"  {idx+1}. Member No: {mem_no} | Name: {mem_name} | Phones: {phones} | Club Code (PLA_CODE): {pla_code} | Room: {flat_num} | Week (FTRA_ID): {ftra_id} | Sleep Rooms: {sleep_room} | Beds: {bed_num}")
            
        conn.close()
    except Exception as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    main()

