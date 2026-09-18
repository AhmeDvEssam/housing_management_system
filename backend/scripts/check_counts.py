import os
import django
import sys
import oracledb
import pandas as pd

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Building
from bookings.models import Booking
from members.models import Member

# Oracle Connection Config
ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def get_oracle_conn():
    try:
        return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    except Exception as e:
        print(f"[ERROR] Could not connect to Oracle: {e}")
        return None

def main():
    conn = get_oracle_conn()
    if not conn:
        return

    cursor = conn.cursor()
    
    # 1. Oracle Counts
    cursor.execute("SELECT COUNT(*) FROM MEMBER")
    oracle_members = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM MEMBER_CONTRACT")
    oracle_contracts = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM PERSON_BOOKED")
    oracle_person_booked = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM FLAT")
    oracle_flats = cursor.fetchone()[0]
    
    # 2. Django Counts
    django_members = Member.objects.count()
    django_bookings = Booking.objects.count()
    
    # Identify legacy buildings
    legacy_buildings = Building.objects.filter(building_type='LEGACY')
    legacy_units = Unit.objects.filter(floor__building__in=legacy_buildings)
    legacy_units_count = legacy_units.count()
    
    print(f"--- RECONCILIATION REPORT ---")
    print(f"Oracle Members: {oracle_members}")
    print(f"Django Members: {django_members}")
    print(f"Discrepancy: {oracle_members - django_members}")
    print("-" * 30)
    print(f"Oracle Contracts (MEMBER_CONTRACT): {oracle_contracts}")
    print(f"Oracle Person Booked (PERSON_BOOKED): {oracle_person_booked}")
    print(f"Total Oracle Records (Potential Bookings): {oracle_contracts + oracle_person_booked}")
    print(f"Django Bookings: {django_bookings}")
    print(f"Discrepancy: {(oracle_contracts + oracle_person_booked) - django_bookings}")
    print("-" * 30)
    print(f"Oracle Flats: {oracle_flats}")
    print(f"Django Legacy Units: {legacy_units_count}")
    print("-" * 30)
    
    # Identify the 8,000 failed records (likely from PERSON_BOOKED or MEMBER_CONTRACT)
    # The user says "8,000 records you couldn't pull".
    
    # Let's see if we can find them.
    # We'll try to fetch all IDs from Oracle and see which ones are missing in Django.
    
    conn.close()

if __name__ == "__main__":
    main()
