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
    
    # 1. MEMBER_CONTRACT
    q1 = """
        SELECT mc.MEM_NO, mc.START_FTRA_DATE, mc.MEMBER_CONTRACT_NUM3, mc.FLAT_ID
        FROM MEMBER_CONTRACT mc
        WHERE EXTRACT(YEAR FROM mc.START_FTRA_DATE) = 2025 AND mc.MEMBER_CONTRACT_FLAG = 1
    """
    cursor.execute(q1)
    mc_rows = cursor.fetchall()
    
    missing = []
    
    for row in mc_rows:
        mem_no, start, cont_num, flat_id = row
        start_d = start.date() if hasattr(start, 'date') else start
        
        # In Django, it might have been merged or saved with guest_id_no=mem_no
        exists = Booking.objects.filter(
            guest_id_no=str(mem_no),
            start_date=start_d,
            status__in=['مؤكد', 'مكتمل']
        ).exists()
        
        if not exists:
            # Let's check by contract_no if available
            if cont_num:
                ex2 = Booking.objects.filter(contract_no=str(cont_num), status__in=['مؤكد', 'مكتمل']).exists()
                if ex2:
                    continue
            missing.append(f"Missing from MEMBER_CONTRACT: Member {mem_no}, Start {start_d}, Contract {cont_num}")

    # 2. PERSON_BOOKED
    q2 = """
        SELECT pb.MEM_NO, pb.PERSON_NAME, pb.BOOKED_START
        FROM PERSON_BOOKED pb
        WHERE EXTRACT(YEAR FROM pb.BOOKED_START) = 2025 AND pb.PERSON_BOOKED_FLAG = 1
    """
    cursor.execute(q2)
    pb_rows = cursor.fetchall()
    
    for row in pb_rows:
        mem_no, p_name, start = row
        start_d = start.date() if hasattr(start, 'date') else start
        
        guest_id = str(mem_no) if mem_no else ""
        
        # Because we merged them, we should just check if ANY booking exists for this guest on this start date
        if guest_id:
            exists = Booking.objects.filter(
                guest_id_no=guest_id,
                start_date__lte=start_d,
                end_date__gte=start_d,
                status__in=['مؤكد', 'مكتمل']
            ).exists()
        else:
            exists = Booking.objects.filter(
                guest_name=p_name,
                start_date__lte=start_d,
                end_date__gte=start_d,
                status__in=['مؤكد', 'مكتمل']
            ).exists()
            
        if not exists:
            missing.append(f"Missing from PERSON_BOOKED: Name {p_name}, ID {mem_no}, Start {start_d}")

    print(f"Total Missing found: {len(missing)}")
    for m in missing[:30]:
        print(m)

except Exception as e:
    print(e)
