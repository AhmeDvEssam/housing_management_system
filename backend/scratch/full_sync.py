import sys
import os
import django
import pandas as pd

# Setup Django
sys.path.append(r'd:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Club, Building, Floor, UnitType, AllocationType

def sync():
    print("--- Starting Full Sync ---")
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

    stats = {'created': 0, 'updated': 0, 'errors': 0}

    for _, row in df.iterrows():
        try:
            club_name = str(row.get('النادي', '')).strip()
            bld_name_raw = str(row.get('رقم العمارة', '')).strip()
            unit_no = str(row.get('رقم الوحدة', '')).strip()
            type_raw = str(row.get('نوع الوحدة', '')).strip()
            class_raw = str(row.get('التصنيف', '')).strip()
            floor_raw = str(row.get('الدور', '')).strip()
            alloc_raw = str(row.get('مخصصات', '')).strip()
            
            if not club_name or not unit_no: continue

            # Normalize building name
            if bld_name_raw.isdigit():
                bld_name = f"عمارة {bld_name_raw}"
            else:
                bld_name = bld_name_raw

            # 1. Get/Create Club
            club, _ = Club.objects.get_or_create(name=club_name)
            
            # 2. Get/Create Building
            building, _ = Building.objects.get_or_create(club=club, name=bld_name)
            
            # 3. Get/Create Floor
            # Try to guess level number from unit_no or floor_raw
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
                # fallback to unit_no first digit if it's 3 digits
                if len(unit_no) >= 3 and unit_no[:-2].isdigit():
                    level = int(unit_no[:-2])

            floor, _ = Floor.objects.get_or_create(building=building, level_number=level, defaults={'label': floor_raw})
            if floor.label != floor_raw:
                floor.label = floor_raw
                floor.save()

            # 4. Get/Create Unit
            unit_type = unit_type_map.get(type_raw, 'APARTMENT_1B')
            allocation = alloc_map.get(alloc_raw, '')
            
            unit, created = Unit.objects.update_or_create(
                floor=floor,
                unit_no=unit_no,
                defaults={
                    'unit_type': unit_type,
                    'classification': class_raw if class_raw != 'nan' else '',
                    'allocation': allocation,
                    'is_bookable': True # Reset to true to avoid status issues
                }
            )
            
            if created:
                stats['created'] += 1
                print(f"Created: {club_name} -> {bld_name} -> {unit_no}")
            else:
                stats['updated'] += 1

        except Exception as e:
            print(f"Error at row {row}: {e}")
            stats['errors'] += 1

    print(f"Sync Complete: {stats}")

if __name__ == '__main__':
    sync()
