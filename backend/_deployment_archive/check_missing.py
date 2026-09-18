import os
import django
import oracledb
import sys

sys.path.append("d:\\housing\\backend")

os.environ["DJANGO_SETTINGS_MODULE"] = "housing.settings"
django.setup()

from bookings.models import Booking
from inventory.models import Unit

def check():
    django_lottery_2026 = Booking.objects.filter(booking_type='LOTTERY', record_date__year=2026).count()
    print(f"Django LOTTERY 2026 count: {django_lottery_2026}")
    
    conn = oracledb.connect("migration_temp/migration@localhost:1521/xe")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM MEMBER_CONTRACT WHERE EXTRACT(YEAR FROM RECORD_DATE) = 2026 AND MEMBER_CONTRACT_TYPE = 9")
    oracle_total = cursor.fetchone()[0]
    print(f"Oracle MEMBER_CONTRACT type 9, 2026 count: {oracle_total}")
    
    cursor.execute("""
        SELECT mc.FLAT_ID, mc.MEM_NO
        FROM MEMBER_CONTRACT mc
        WHERE EXTRACT(YEAR FROM mc.RECORD_DATE) = 2026 AND mc.MEMBER_CONTRACT_TYPE = 9
    """)
    oracle_rows = cursor.fetchall()
    
    missing_flat_in_oracle_flat_table = 0
    missing_club_in_map = 0
    missing_unit_in_django = 0
    
    for flat_id, mem_no in oracle_rows:
        cursor.execute("SELECT PLA_CODE, FLAT_NUM FROM FLAT WHERE FLAT_ID = :1", (flat_id,))
        flat_row = cursor.fetchone()
        if not flat_row:
            missing_flat_in_oracle_flat_table += 1
            continue
            
        pla_code, flat_num = flat_row
        
        # Check if unit exists in Django
        # The script does: unit = Unit.objects.filter(club__id=club_id, name=str(flat_num)).first()
        unit_exists = Unit.objects.filter(club__id=pla_code, name=str(flat_num)).exists()
        if not unit_exists:
            missing_unit_in_django += 1
            
    print(f"Missing FLAT_ID in Oracle FLAT table: {missing_flat_in_oracle_flat_table}")
    print(f"Missing Unit in Django (likely deleted during reset-units): {missing_unit_in_django}")

if __name__ == "__main__":
    check()
