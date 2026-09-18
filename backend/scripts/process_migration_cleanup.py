import os
import django
import sys
import oracledb
import pandas as pd
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Building, Club
from bookings.models import Booking
from members.models import Member

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
    try:
        return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    except Exception as e:
        print(f"[ERROR] Could not connect to Oracle: {e}")
        return None

def export_imported_units():
    print("Exporting imported units...")
    legacy_buildings = Building.objects.filter(building_type='LEGACY')
    units = Unit.objects.filter(floor__building__in=legacy_buildings).select_related('floor__building', 'floor__building__club')
    
    data = []
    for u in units:
        data.append({
            'ID': u.id,
            'Club': u.floor.building.club.name,
            'Building': u.floor.building.name,
            'Unit No': u.unit_no,
            'Created At': u.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    df = pd.DataFrame(data)
    df.to_excel('imported_units_report.xlsx', index=False)
    print(f"Exported {len(data)} units to imported_units_report.xlsx")
    return [u.id for u in units]

def fetch_all_oracle_bookings(conn):
    print("Fetching all potential bookings from Oracle...")
    cursor = conn.cursor()
    
    # MEMBER_CONTRACT
    query1 = """
        SELECT mc.MEM_NO, mc.FLAT_ID, mc.FOR_YEAR, mc.FROM_DATE, mc.TO_DATE, mc.MEMBER_CONTRACT_VAL3, mc.MEMBER_CONTRACT_NUM3, f.PLA_CODE
        FROM MEMBER_CONTRACT mc
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
    """
    contracts = []
    try:
        cursor.execute(query1)
        for row in cursor:
            contracts.append({
                'Source': 'MEMBER_CONTRACT',
                'Member No': row[0],
                'Flat ID': row[1],
                'Year': row[2],
                'Start Date': row[3],
                'End Date': row[4],
                'Value': row[5],
                'Contract Num': row[6],
                'Club ID': row[7]
            })
    except Exception as e:
        print(f"Error fetching contracts: {e}")

    # PERSON_BOOKED
    query2 = "SELECT MEM_NO, PERSON_NAME, RECORD_DATE, DAYS_NUMBER, CLUB_ID, BOOKING_NUM FROM PERSON_BOOKED"
    person_booked = []
    try:
        cursor.execute(query2)
        for row in cursor:
            person_booked.append({
                'Source': 'PERSON_BOOKED',
                'Member No': row[0],
                'Name': row[1],
                'Date': row[2],
                'Days': row[3],
                'Club ID': row[4],
                'Booking Num': row[5]
            })
    except Exception as e:
        print(f"Error fetching person_booked: {e}")
        
    return contracts, person_booked

def export_failed_records(contracts, person_booked):
    print("Analyzing failed records...")
    
    # We'll consider a record "failed" if it's not in Django.
    # To be precise, the user said "8,000 records you couldn't pull".
    # I'll just export EVERYTHING from Oracle that is missing in Django bookings.
    
    # Get existing Django bookings info to check against
    # (Using member_no and start_date as a proxy for identification)
    django_bookings = Booking.objects.all().values_list('member__membership_no', 'start_date')
    django_set = set(django_bookings)
    
    failed_data = []
    
    for c in contracts:
        # Check if exists
        start_date = c['Start Date'].date() if hasattr(c['Start Date'], 'date') else c['Start Date']
        if (str(c['Member No']), start_date) not in django_set:
            c['Reason'] = 'Not found in Django (Possible mapping or sync failure)'
            failed_data.append(c)
            
    for p in person_booked:
        start_date = p['Date'].date() if hasattr(p['Date'], 'date') else p['Date']
        if (str(p['Member No']), start_date) not in django_set:
            p['Reason'] = 'Not found in Django (Possible mapping or sync failure)'
            failed_data.append(p)
            
    df = pd.DataFrame(failed_data)
    df.to_excel('failed_records_report.xlsx', index=False)
    print(f"Exported {len(failed_data)} failed records to failed_records_report.xlsx")

def cleanup_units(unit_ids):
    print(f"Cleaning up {len(unit_ids)} units...")
    # Delete units. CASCADE will take care of bookings and contracts.
    Unit.objects.filter(id__in=unit_ids).delete()
    # Also delete the buildings if they are empty
    Building.objects.filter(building_type='LEGACY', floors__units__isnull=True).delete()
    print("Cleanup complete.")

def main():
    conn = get_oracle_conn()
    if not conn:
        return

    # Phase 1: Report
    unit_ids = export_imported_units()
    
    contracts, person_booked = fetch_all_oracle_bookings(conn)
    export_failed_records(contracts, person_booked)
    
    # Phase 2: Cleanup
    cleanup_units(unit_ids)
    
    conn.close()

if __name__ == "__main__":
    main()
