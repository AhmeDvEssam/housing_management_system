import os
import sys
import io
import json
import oracledb
import django
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

def compare():
    club_map = json.load(open(r'D:\housing\backend\scripts\club_map.json', encoding='utf-8'))

    conn = oracledb.connect(user="migration_temp", password="migration", dsn="localhost/xe")
    cursor = conn.cursor()
    
    query = """
        SELECT mc.MEM_NO, f.PLA_CODE, f.FLAT_NUM, mc.START_FTRA_DATE, mc.END_FTRA_DATE, 'MEMBER_CONTRACT' as SRC
        FROM MEMBER_CONTRACT mc
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
        WHERE EXTRACT(YEAR FROM mc.RECORD_DATE) = 2025 AND mc.MEMBER_CONTRACT_FLAG = 1
    """
    cursor.execute(query)
    mc_rows = cursor.fetchall()
    
    query2 = """
        SELECT pb.MEM_NO, f.PLA_CODE, f.FLAT_NUM, pb.BOOKED_START, pb.BOOKED_END, 'PERSON_BOOKED' as SRC
        FROM PERSON_BOOKED pb
        JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID
        WHERE EXTRACT(YEAR FROM pb.RECORD_DATE) = 2025 AND pb.PERSON_BOOKED_FLAG = 1
    """
    cursor.execute(query2)
    pb_rows = cursor.fetchall()
    
    cursor.close()
    conn.close()

    oracle_records = []
    for i, r in enumerate(mc_rows + pb_rows):
        pla_code = str(r[1]) if r[1] else ""
        club_name = club_map.get(pla_code, "")
        
        oracle_records.append({
            'mem_no': str(r[0]) if r[0] else "",
            'club_name': club_name,
            'flat_num': str(r[2]) if r[2] else "",
            'start_date': r[3].date() if r[3] else None,
            'end_date': r[4].date() if r[4] else None,
            'src': r[5],
        })
        
    print(f"Oracle fetched: {len(oracle_records)}")
    
    django_qs = Booking.objects.filter(record_date__year=2025, status='مؤكد').select_related('unit__floor__building__club')
    django_records = []
    for b in django_qs:
        django_records.append({
            'mem_no': str(b.member.membership_no) if b.member else str(b.guest_id_no),
            'club_name': b.unit.floor.building.club.name,
            'flat_num': str(b.unit.unit_no),
            'start_date': b.start_date,
            'end_date': b.end_date,
            'id': b.id
        })
        
    print(f"Django fetched: {len(django_records)}")
    
    missing_in_django = []
    unmatched_django = list(django_records)
    
    for orc in oracle_records:
        matched = False
        
        # 1. Exact match on club, flat, dates
        for d in unmatched_django:
            if (orc['club_name'] == d['club_name'] and
                orc['flat_num'] == d['flat_num'] and
                orc['start_date'] == d['start_date'] and
                orc['end_date'] == d['end_date']):
                unmatched_django.remove(d)
                matched = True
                break
                
        # 2. Fuzzy date match on club, flat
        if not matched:
            for d in unmatched_django:
                if (orc['club_name'] == d['club_name'] and
                    orc['flat_num'] == d['flat_num']):
                    if d['start_date'] and orc['start_date']:
                        diff = abs((d['start_date'] - orc['start_date']).days)
                        if diff < 10:
                            unmatched_django.remove(d)
                            matched = True
                            break
                            
        if not matched:
            missing_in_django.append(orc)

    with open(r'D:\housing\backend\scratch\diff_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"Missing in Django: {len(missing_in_django)}\n")
        for m in missing_in_django:
            f.write(f"SRC={m['src']} | Mem={m['mem_no']} | Club={m['club_name']} | Flat={m['flat_num']} | Dates={m['start_date']} to {m['end_date']}\n")
            
        f.write(f"\nExtra in Django: {len(unmatched_django)}\n")
        for d in unmatched_django:
            f.write(f"ID={d['id']} | Mem={d['mem_no']} | Club={d['club_name']} | Flat={d['flat_num']} | Dates={d['start_date']} to {d['end_date']}\n")

if __name__ == "__main__":
    compare()
