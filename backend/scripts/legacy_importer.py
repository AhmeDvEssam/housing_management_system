import os
import django
import sys
import csv
from datetime import datetime

# Setup Django
sys.path.append('d:\\housing\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from django.db import transaction
from members.models import Member, FamilyMember
from inventory.models import Club, Building, Floor, Unit
from bookings.models import Booking, Contract

# Mapping Dictionaries
CLUB_MAP = {
    '7': 1, # Port Said
    '8': 2, # Ras El Bar
    '4': 3, # Fayed
    '5': 4, # Gamasa
    '2': 5, # Anfoushi
}

RELATION_MAP = {
    '1': 'والد',
    '2': 'والدة',
    '3': 'العم',
    '4': 'الخال',
    '5': 'نجل',
    '6': 'كريمة',
    '7': 'الزوج',
    '8': 'الجده',
    '9': 'الزوجة',
    '11': 'الاخ',
    '12': 'الاخت',
}

UNIT_MAP = {} # (club_id, unit_no) -> new_unit_id
LEGACY_FLAT_MAP = {} # legacy_flat_id -> new_unit_id
MEMBER_ID_MAP = {} # legacy_mem_no -> new_member_id

def load_unit_map():
    print("Loading unit map...")
    for unit in Unit.objects.select_related('floor__building__club').all():
        key = (unit.floor.building.club.id, unit.unit_no)
        UNIT_MAP[key] = unit.id
    print(f"Loaded {len(UNIT_MAP)} units.")

def get_or_create_legacy_unit(club_id, unit_no):
    # Try to find in existing units
    unit_id = UNIT_MAP.get((club_id, unit_no))
    if unit_id:
        return unit_id
    
    # Otherwise, create in a special building
    club = Club.objects.get(id=club_id)
    building, _ = Building.objects.get_or_create(
        club=club, name="وحدات قديمة المستوردة",
        defaults={'building_type': 'LEGACY'}
    )
    floor, _ = Floor.objects.get_or_create(
        building=building, level_number=0,
        defaults={'label': 'مستورد'}
    )
    unit, created = Unit.objects.get_or_create(
        floor=floor, unit_no=unit_no,
        defaults={'unit_type': 'APARTMENT_1B', 'classification': 'مستورد'}
    )
    
    UNIT_MAP[(club_id, unit_no)] = unit.id
    return unit.id

def load_legacy_flat_mapping():
    print("Loading legacy flat mapping...")
    count = 0
    with open('d:\\dmp\\scratch\\flat_mapping.csv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 3:
                l_flat_id, l_flat_num, l_pla_code = parts[0], parts[1], parts[2]
                new_club_id = CLUB_MAP.get(l_pla_code)
                if new_club_id:
                    unit_id = get_or_create_legacy_unit(new_club_id, l_flat_num)
                    if unit_id:
                        LEGACY_FLAT_MAP[l_flat_id] = unit_id
                        count += 1
    print(f"Mapped {count} legacy flats to units (including created ones).")

def import_members():
    print("Importing members...")
    count = 0
    with open('d:\\dmp\\scratch\\members_export_pipe.csv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 2:
                l_mem_no = parts[0]
                l_name = parts[1]
                l_nat_id = parts[2] if len(parts) > 2 else ""
                l_phone = parts[3] if len(parts) > 3 else ""
                l_rank = parts[4] if len(parts) > 4 else ""
                l_addr = parts[5] if len(parts) > 5 else ""

                member, created = Member.objects.update_or_create(
                    membership_no=l_mem_no,
                    defaults={
                        'full_name': l_name,
                        'national_id': l_nat_id,
                        'phone': l_phone,
                        'rank': l_rank,
                        'address': l_addr,
                    }
                )
                MEMBER_ID_MAP[l_mem_no] = member.id
                count += 1
                if count % 1000 == 0:
                    print(f"Processed {count} members...")
    print(f"Finished importing {count} members.")

def import_family():
    print("Importing family members...")
    count = 0
    with open('d:\\dmp\\scratch\\family_export_pipe.csv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 3:
                l_cust_id = parts[0]
                l_name = parts[1]
                l_rel_type = parts[2]
                l_nat_id = parts[3] if len(parts) > 3 else ""

                member_id = MEMBER_ID_MAP.get(l_cust_id)
                if member_id:
                    FamilyMember.objects.get_or_create(
                        member_id=member_id,
                        name=l_name,
                        relation=RELATION_MAP.get(l_rel_type, f"كود {l_rel_type}"),
                        defaults={
                            'national_id': l_nat_id,
                        }
                    )
                    count += 1
                    if count % 1000 == 0:
                        print(f"Processed {count} family members...")
    print(f"Finished importing {count} family members.")

MONTHS_EN = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
             'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

def parse_oracle_date(date_str):
    if not date_str or date_str == 'None':
        return None
    try:
        parts = date_str.split('-')
        if len(parts) == 3:
            day = int(parts[0])
            month = MONTHS_EN.get(parts[1].upper(), 1)
            year_val = int(parts[2])
            year = year_val + 2000 if year_val < 70 else year_val + 1900
            return datetime(year, month, day).date()
    except:
        pass
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def import_contracts():
    print("Importing contracts as bookings...")
    count = 0
    with open('d:\\dmp\\scratch\\contracts_export_pipe.csv', 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 5:
                l_mem_no = parts[0]
                l_flat_id = parts[1]
                l_year = parts[2]
                l_from = parts[3]
                l_to = parts[4]
                l_price = parts[5] if len(parts) > 5 else "0"

                member_id = MEMBER_ID_MAP.get(l_mem_no)
                unit_id = LEGACY_FLAT_MAP.get(l_flat_id)

                if member_id and unit_id:
                    start_date = parse_oracle_date(l_from)
                    end_date = parse_oracle_date(l_to)
                    if not start_date or not end_date:
                        continue

                    booking = Booking.objects.create(
                        member_id=member_id,
                        unit_id=unit_id,
                        start_date=start_date,
                        end_date=end_date,
                        total_price=float(l_price) if l_price else 0,
                        status="مؤكد (مستورد)",
                    )
                    Contract.objects.create(
                        booking=booking,
                        contract_no=f"LEGACY-{l_mem_no}-{l_year}",
                        is_signed=True,
                    )
                    count += 1
                    if count % 500 == 0:
                        print(f"Processed {count} contracts...")
    print(f"Finished importing {count} contracts.")

if __name__ == "__main__":
    load_unit_map()
    load_legacy_flat_mapping()
    
    import_members()
    import_family()
    import_contracts()
    
    print("ALL DATA IMPORTED SUCCESSFULLY!")
