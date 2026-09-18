import sys
import os
import django
import pandas as pd

# Setup Django
sys.path.append(r'd:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Club, Building, Floor
from bookings.models import BookingDay

def master_sync():
    print("--- Starting Clean Master Sync ---")
    df = pd.read_excel(r'd:\housing\Data.xlsx', sheet_name='data')
    
    # 1. Identify Clubs to sync
    synced_club_names = [str(c).strip() for c in df['النادي'].unique()]
    print(f"Syncing clubs: {synced_club_names}")

    # 2. Identify Units with bookings to preserve
    booked_unit_ids = list(BookingDay.objects.values_list('unit_id', flat=True).distinct())
    print(f"Preserving {len(booked_unit_ids)} units with bookings.")

    # 3. DELETE all units for these clubs (except those with bookings)
    deleted_units, _ = Unit.objects.filter(floor__building__club__name__in=synced_club_names).exclude(id__in=booked_unit_ids).delete()
    print(f"Deleted {deleted_units} redundant units.")

    # 4. Perform Sync
    unit_type_map = {
        'شقة 1 غرفة': 'APARTMENT_1B',
        'شقة 2 غرفة': 'APARTMENT_2B',
        'غرفة': 'ROOM',
        'جناح': 'SUITE',
    }
    
    alloc_map = {
        'اسكان إداري': 'ADMINISTRATIVE',
        'سكن إداري': 'ADMINISTRATIVE',
        'اسكان إدارى': 'ADMINISTRATIVE',
        'مخصصات القائد': 'COMMANDER',
        'مخصصات الشركات': 'COMPANY',
        'اسكان دائم عقود': 'PERMANENT'
    }

    stats = {'created': 0, 'updated': 0}

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

            # Normalization
            bld_name = bld_name_raw
            if bld_name.isdigit():
                bld_name = f"عمارة {bld_name}"

            club, _ = Club.objects.get_or_create(name=club_name)
            
            # Find building (avoid fuzzy matches that might lead to wrong names)
            building, _ = Building.objects.get_or_create(club=club, name=bld_name)
            
            # Floor level identification
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

            unit_type = unit_type_map.get(type_raw, 'APARTMENT_1B')
            allocation = alloc_map.get(alloc_raw, '')
            
            # Update or Create
            # We use floor and unit_no as unique identifier for creation
            unit, created = Unit.objects.update_or_create(
                floor=floor,
                unit_no=unit_no,
                defaults={
                    'unit_type': unit_type,
                    'classification': class_raw if class_raw != 'nan' else '',
                    'allocation': allocation,
                    'is_bookable': True
                }
            )
            
            if created: stats['created'] += 1
            else: stats['updated'] += 1

        except Exception as e:
            print(f"Error at row {unit_no}: {e}")

    print(f"Master Sync Complete. {stats}")

if __name__ == '__main__':
    master_sync()
