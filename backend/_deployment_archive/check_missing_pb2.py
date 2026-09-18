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
    
    # 2. PERSON_BOOKED missing
    q2 = """
        SELECT pb.PERSON_NAME, pb.BOOKED_START, f.PLA_CODE, f.FLAT_NUM, f.FLAT_ID, pb.MEM_NO, pb.BOOKED_END
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
        name, start, club_id, flat_num, flat_id, mem_no, end = row
        dstr = start.strftime("%Y-%m-%d")
        if dstr in ['2025-10-16', '2025-11-06', '2025-10-24', '2025-08-20']:
            print(f"Name: {name}, Date: {start}, End: {end}, ClubID: {club_id}, FlatNum: {flat_num}, FlatID: {flat_id}, Mem_No: {mem_no}")
            unit = get_unit_from_our_db(cursor, club_id, flat_num)
            if unit:
                print(f"  -> Django Unit exists! {unit.floor.building.club.name} - {unit.unit_no}")
            else:
                print(f"  -> Django Unit NOT FOUND. It was skipped because it doesn't exist in our Data.xlsx.")
            
            # Check if this exact booking was skipped due to duplicate guest_name, guest_id_no, start, end regardless of unit
            guest_id_val = str(mem_no) if mem_no else ""
            guest_name_val = str(name)[:200]
            existing = Booking.objects.filter(
                guest_name=guest_name_val,
                guest_id_no=guest_id_val,
                start_date=start,
                end_date=end
            ).exists()
            print(f"  -> Existing duplicate by name/dates? {existing}")

except Exception as e:
    import traceback
    traceback.print_exc()
