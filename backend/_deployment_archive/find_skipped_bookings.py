import os, django, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

import oracledb
from bookings.models import Booking
from members.models import Member

ORACLE_USER = 'MIGRATION_TEMP'
ORACLE_PASS = 'migration'
ORACLE_DSN = 'localhost:1521/xe'

try:
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    query = """
        SELECT pb.MEM_NO, pb.PERSON_NAME, pb.BOOKED_START, pb.BOOKED_END
        FROM PERSON_BOOKED pb
        WHERE EXTRACT(YEAR FROM pb.BOOKED_START) = 2025 AND pb.PERSON_BOOKED_FLAG = 1
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    skipped_or_merged = []
    
    for row in rows:
        mem_no, person_name, booked_start, booked_end = row
        start = booked_start.date() if hasattr(booked_start, 'date') else booked_start
        end = booked_end.date() if hasattr(booked_end, 'date') else booked_end
        
        member = Member.objects.filter(membership_no=str(mem_no)).first()
        
        # Check if overlapping contract exists
        existing_contract = False
        if member:
            existing_contract = Booking.objects.filter(
                member=member,
                start_date__lte=start,
                end_date__gte=end
            ).exists()
            
        if existing_contract:
            skipped_or_merged.append(f"Merged with contract: Member No {mem_no}, Name {person_name or member.full_name}, Dates: {start} to {end}")
            continue
            
        # Check if duplicate exact exists
        guest_name_val = str(person_name)[:200] if person_name else (member.full_name if member else f"ضيف غير مسجل ({mem_no})")
        guest_id_val = str(mem_no) if mem_no else ""
        
        existing_exact = Booking.objects.filter(
            guest_name=guest_name_val,
            guest_id_no=guest_id_val,
            start_date=start,
            end_date=end
        ).exists()
        
        if existing_exact:
            # We must check if this exact booking was actually synced as a SINGLE booking. 
            # If there are duplicates in Oracle itself, the first one is synced, the second one is skipped.
            # To test if it's a duplicate IN Oracle, we can't just check existing_exact, because the FIRST one will also have existing_exact=True now.
            # But we know there were 4 skipped duplicates and 5 merges.
            pass

    print("Merged Bookings:")
    for s in skipped_or_merged:
        print(s)
        
    # Find duplicates in Oracle PERSON_BOOKED
    query_dupes = """
        SELECT pb.MEM_NO, pb.PERSON_NAME, pb.BOOKED_START, pb.BOOKED_END, COUNT(*)
        FROM PERSON_BOOKED pb
        WHERE EXTRACT(YEAR FROM pb.BOOKED_START) = 2025 AND pb.PERSON_BOOKED_FLAG = 1
        GROUP BY pb.MEM_NO, pb.PERSON_NAME, pb.BOOKED_START, pb.BOOKED_END
        HAVING COUNT(*) > 1
    """
    cursor.execute(query_dupes)
    dupes = cursor.fetchall()
    print("\\nDuplicate Bookings in PERSON_BOOKED:")
    for d in dupes:
        print(f"Duplicate found {d[4]} times: Member No {d[0]}, Name {d[1]}, Dates: {d[2]} to {d[3]}")

except Exception as e:
    print(e)
