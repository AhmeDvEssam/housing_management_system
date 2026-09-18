import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

import django
django.setup()

import oracledb
from bookings.models import Booking
from inventory.models import Unit, Club
from scripts.smart_sync_final import get_unit_from_our_db

ORACLE_USER = 'MIGRATION_TEMP'
ORACLE_PASS = 'migration'
ORACLE_DSN = 'localhost:1521/xe'

try:
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    # 1. MEMBER_CONTRACT missing
    q1 = """
        SELECT mc.MEM_NO, mc.START_FTRA_DATE, mc.MEMBER_CONTRACT_NUM3, f.PLA_CODE, f.FLAT_NUM, f.FLAT_ID
        FROM MEMBER_CONTRACT mc
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
        WHERE EXTRACT(YEAR FROM mc.START_FTRA_DATE) = 2025 AND mc.MEMBER_CONTRACT_FLAG = 1
        AND mc.MEM_NO IN (13990, 23728, 34241)
    """
    cursor.execute(q1)
    mc_rows = cursor.fetchall()
    print("MEMBER_CONTRACT Missing Check:")
    for row in mc_rows:
        mem, start, cnum, club_id, flat_num, flat_id = row
        print(f"Mem: {mem}, Date: {start}, ClubID: {club_id}, FlatNum: {flat_num}, FlatID: {flat_id}")
        unit = get_unit_from_our_db(cursor, club_id, flat_num)
        if unit:
            print(f"  -> Django Unit exists! {unit.club.name} - {unit.number}")
        else:
            print(f"  -> Django Unit NOT FOUND. It was skipped because it doesn't exist in our Data.xlsx.")

    # 2. PERSON_BOOKED missing
    q2 = """
        SELECT pb.PERSON_NAME, pb.BOOKED_START, f.PLA_CODE, f.FLAT_NUM, f.FLAT_ID
        FROM PERSON_BOOKED pb
        JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID
        WHERE EXTRACT(YEAR FROM pb.BOOKED_START) = 2025 AND pb.PERSON_BOOKED_FLAG = 1
        AND (
            pb.PERSON_NAME LIKE '%الاحمدى%' OR 
            pb.MEM_NO = 7855
        )
    """
    cursor.execute(q2)
    pb_rows = cursor.fetchall()
    print("\\nPERSON_BOOKED Missing Check:")
    for row in pb_rows:
        name, start, club_id, flat_num, flat_id = row
        dstr = start.strftime("%Y-%m-%d")
        if dstr in ['2025-10-16', '2025-11-06', '2025-10-24', '2025-08-20']:
            print(f"Name: {name}, Date: {start}, ClubID: {club_id}, FlatNum: {flat_num}, FlatID: {flat_id}")
            unit = get_unit_from_our_db(cursor, club_id, flat_num)
            if unit:
                print(f"  -> Django Unit exists! {unit.club.name} - {unit.number}")
            else:
                print(f"  -> Django Unit NOT FOUND. It was skipped because it doesn't exist in our Data.xlsx.")

except Exception as e:
    import traceback
    traceback.print_exc()
