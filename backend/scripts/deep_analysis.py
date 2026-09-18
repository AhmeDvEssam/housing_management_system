import os
import django
import sys
import oracledb
import pandas as pd

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club, Unit, Building
from bookings.models import Booking

# Oracle Connection Config
ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

CLUB_MAP = {
    7: 1, # Port Said
    8: 2, # Ras El Bar
    4: 3, # Fayed
    5: 4, # Gamasa
    2: 5, # Anfoushi
}

def get_oracle_conn():
    return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)

def analyze():
    conn = get_oracle_conn()
    cursor = conn.cursor()
    
    # 1. Club Analysis
    print("Analyzing Clubs...")
    cursor.execute("SELECT PLA_CODE, COUNT(*) FROM FLAT GROUP BY PLA_CODE")
    oracle_clubs_data = cursor.fetchall()
    
    club_analysis = []
    for code, flat_count in oracle_clubs_data:
        django_id = CLUB_MAP.get(code)
        django_club_name = "N/A"
        if django_id:
            try:
                django_club_name = Club.objects.get(id=django_id).name
            except:
                django_club_name = f"ID {django_id} (Not found in DB)"
        
        club_analysis.append({
            'Oracle PLA_CODE': code,
            'Oracle Flat Count': flat_count,
            'Mapped to Django Club ID': django_id if django_id else 'MISSING',
            'Django Club Name': django_club_name
        })
    
    # 2. Detailed Booking Breakdown
    print("Analyzing Bookings Breakdown...")
    cursor.execute("SELECT CLUB_ID, COUNT(*) FROM PERSON_BOOKED GROUP BY CLUB_ID")
    pb_counts = dict(cursor.fetchall())
    
    # We need to join MEMBER_CONTRACT with FLAT to get club
    cursor.execute("""
        SELECT f.PLA_CODE, COUNT(*) 
        FROM MEMBER_CONTRACT mc 
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID 
        GROUP BY f.PLA_CODE
    """)
    mc_counts = dict(cursor.fetchall())
    
    all_codes = set(list(pb_counts.keys()) + list(mc_counts.keys()))
    booking_analysis = []
    for code in all_codes:
        booking_analysis.append({
            'Oracle Club ID': code,
            'Contracts Count': mc_counts.get(code, 0),
            'Person Booked Count': pb_counts.get(code, 0),
            'Total Records': mc_counts.get(code, 0) + pb_counts.get(code, 0),
            'Status': 'Mapped' if code in CLUB_MAP else 'UNMAPPED (Data Lost)'
        })

    # 3. Flat Mapping Discrepancies
    print("Analyzing Flat Mappings...")
    cursor.execute("SELECT FLAT_ID, FLAT_NUM, PLA_CODE FROM FLAT")
    all_flats = cursor.fetchall()
    flat_data = []
    for f_id, f_num, p_code in all_flats:
        django_club_id = CLUB_MAP.get(p_code)
        match_found = False
        if django_club_id:
            # Check if unit exists in Django
            unit = Unit.objects.filter(floor__building__club_id=django_club_id, unit_no=str(f_num)).first()
            if unit:
                match_found = True
        
        flat_data.append({
            'Oracle FLAT_ID': f_id,
            'Oracle FLAT_NUM': f_num,
            'Oracle PLA_CODE': p_code,
            'Django Club ID': django_club_id,
            'Matched in Django?': 'Yes' if match_found else 'No'
        })

    # Export to Excel with multiple sheets
    with pd.ExcelWriter('migration_deep_analysis.xlsx') as writer:
        pd.DataFrame(club_analysis).to_excel(writer, sheet_name='Clubs Analysis', index=False)
        pd.DataFrame(booking_analysis).to_excel(writer, sheet_name='Bookings Loss Analysis', index=False)
        pd.DataFrame(flat_data).to_excel(writer, sheet_name='Flats Mapping', index=False)
        
    print("Analysis complete. Saved to migration_deep_analysis.xlsx")
    conn.close()

if __name__ == "__main__":
    analyze()
