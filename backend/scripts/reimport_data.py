import os
import sys
import django
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Club, Building, Floor

def reimport_data(file_path):
    print(f"Reading data from {file_path}")
    df = pd.read_excel(file_path)
    
    # Assume columns: Club, Building, Unit, Classification, View, Capacity (or similar)
    # The user mentioned classifications changed.
    
    for _, row in df.iterrows():
        try:
            club_name = str(row.get('النادي', '')).strip()
            building_input = str(row.get('رقم العمارة', '')).strip()
            unit_no = str(row.get('رقم الوحدة', '')).strip()
            classification = str(row.get('التصنيف', '')).strip()
            
            unit_type_raw = str(row.get('نوع الوحدة', '')).strip()
            allocation_raw = str(row.get('مخصصات', '')).strip()
            floor_raw = str(row.get('الدور', '')).strip()
            
            # map unit type
            unit_type_map = {
                'شقة 1 غرفة': 'APARTMENT_1B',
                'شقة 2 غرفة': 'APARTMENT_2B',
                'غرفة': 'ROOM',
                'جناح': 'SUITE',
            }
            unit_type = unit_type_map.get(unit_type_raw, 'APARTMENT_1B')
            
            # map allocation
            allocation_map = {
                'اسكان إداري': 'ADMINISTRATIVE',
                'سكن إداري': 'ADMINISTRATIVE',
                'اسكان إدارى': 'ADMINISTRATIVE',
                'مخصصات القائد': 'COMMANDER',
                'مخصصات الشركات': 'COMPANY',
                'اسكان دائم عقود': 'PERMANENT'
            }
            allocation = allocation_map.get(allocation_raw, '')
            
            # Normalize building name (e.g. if input is '1' but name is 'عمارة 1')
            if not building_input.startswith('عمارة'):
                building_name = f"عمارة {building_input}"
            else:
                building_name = building_input
            
            # Find the unit
            unit = Unit.objects.filter(
                unit_no=unit_no,
                floor__building__name__icontains=building_input, # Use icontains for flexibility
                floor__building__club__name=club_name
            ).first()
            
            if unit:
                if classification: unit.classification = classification
                if allocation: unit.allocation = allocation
                unit.unit_type = unit_type
                # try to update floor label if provided
                if floor_raw and floor_raw != 'nan':
                    unit.floor.label = floor_raw
                    unit.floor.save()
                    
                unit.save()
                print(f"Updated unit {unit_no} in {building_name} ({club_name})")
            else:
                print(f"Unit {unit_no} not found in {building_name} / {club_name}")
                
        except Exception as e:
            print(f"Error processing row: {e}")

if __name__ == "__main__":
    file_path = r"d:\housing\Data.xlsx"
    reimport_data(file_path)
