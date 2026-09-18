import sys
import os
import django
import pandas as pd

# Setup Django
sys.path.append(r'd:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Club, Building, Floor
from bookings.models import Booking

def master_sync():
    print("--- Starting Master Sync (Absolute Truth: Excel) ---")
    df = pd.read_excel(r'd:\housing\Data.xlsx', sheet_name='data')
    
    # Mapping for Unit Types
    unit_type_map = {
        'شقة 1 غرفة': 'APARTMENT_1B',
        'شقة 2 غرفة': 'APARTMENT_2B',
        'غرفة': 'ROOM',
        'جناح': 'SUITE',
    }
    
    # Mapping for Allocations
    alloc_map = {
        'اسكان إداري': 'ADMINISTRATIVE',
        'سكن إداري': 'ADMINISTRATIVE',
        'اسكان إدارى': 'ADMINISTRATIVE',
        'مخصصات القائد': 'COMMANDER',
        'مخصصات الشركات': 'COMPANY',
        'اسكان دائم عقود': 'PERMANENT'
    }

    seen_unit_ids = set()
    synced_clubs = set()

    for _, row in df.iterrows():
        try:
            club_name = " ".join(str(row.get('النادي', '')).split())
            bld_name_raw = " ".join(str(row.get('رقم العمارة', '')).split())
            unit_no = str(row.get('رقم الوحدة', '')).strip()
            type_raw = str(row.get('نوع الوحدة', '')).strip()
            class_raw = str(row.get('التصنيف', '')).strip()
            floor_raw = str(row.get('الدور', '')).strip()
            alloc_raw = str(row.get('مخصصات', '')).strip()
            
            if not club_name or not unit_no or unit_no == 'nan': continue
            
            synced_clubs.add(club_name)

            # 1. Normalize building name
            bld_name = bld_name_raw
            if bld_name.isdigit():
                bld_name = f"عمارة {bld_name}"

            # 2. Get/Create Club
            club, _ = Club.objects.get_or_create(name=club_name)
            
            # 3. Get/Create Building
            # Try to find existing building with similar name first to avoid duplicates
            building = Building.objects.filter(club=club, name__icontains=bld_name_raw).first()
            if not building:
                building, _ = Building.objects.get_or_create(club=club, name=bld_name)
            else:
                # Update name to the one in Excel if it's different
                if building.name != bld_name:
                    building.name = bld_name
                    building.save()
            
            # 4. Get/Create Floor
            level = 0
            if 'ارضي' in floor_raw: level = 0
            elif 'اول' in floor_raw: level = 1
            elif 'ثاني' in floor_raw: level = 2
            elif 'ثالث' in floor_raw: level = 3
            elif 'رابع' in floor_raw: level = 4
            elif 'خامس' in floor_raw: level = 5
            elif 'سادس' in floor_raw: level = 6
            elif 'سابع' in floor_raw: level = 7
            elif 'ثامن' in floor_raw: level = 8
            elif 'تاسع' in floor_raw: level = 9
            elif 'عاشر' in floor_raw: level = 10
            else:
                if len(unit_no) >= 3 and unit_no[:-2].isdigit():
                    level = int(unit_no[:-2])

            floor, _ = Floor.objects.get_or_create(building=building, level_number=level, defaults={'label': floor_raw})
            if floor.label != floor_raw:
                floor.label = floor_raw
                floor.save()

            # 5. Sync Unit
            unit_type = unit_type_map.get(type_raw, 'APARTMENT_1B')
            allocation = alloc_map.get(alloc_raw, '')
            
            # Search for unit by number and club (wide search to avoid duplicates across buildings)
            # But the constraint is unique per floor.
            # We want to find the unit if it already exists ANYWHERE in the club to move it if needed.
            unit = Unit.objects.filter(unit_no=unit_no, floor__building__club=club).first()
            
            if unit:
                unit.floor = floor # Move to correct building/floor
                unit.unit_type = unit_type
                unit.classification = class_raw if class_raw != 'nan' else ''
                unit.allocation = allocation
                unit.is_bookable = True
                unit.save()
            else:
                unit = Unit.objects.create(
                    floor=floor,
                    unit_no=unit_no,
                    unit_type=unit_type,
                    classification=class_raw if class_raw != 'nan' else '',
                    allocation=allocation,
                    is_bookable=True
                )
            
            seen_unit_ids.add(unit.id)

        except Exception as e:
            print(f"Error processing row: {e}")

    # CLEANUP: Delete units in synced clubs that were not in Excel
    print(f"Synced clubs: {synced_clubs}")
    untouched_units = Unit.objects.filter(floor__building__club__name__in=synced_clubs).exclude(id__in=seen_unit_ids)
    
    deleted_count = 0
    for u in untouched_units:
        # Check for bookings
        if u.booking_days.exists():
            print(f"WARNING: Cannot delete unit {u.unit_no} (Club: {u.floor.building.club.name}) because it has bookings. Marking as non-bookable instead.")
            u.is_bookable = False
            u.save()
        else:
            u.delete()
            deleted_count += 1
            
    print(f"Master Sync Complete. Units created/updated: {len(seen_unit_ids)}, Units deleted: {deleted_count}")

if __name__ == '__main__':
    master_sync()
