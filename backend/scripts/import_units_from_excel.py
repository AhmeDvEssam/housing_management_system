import os
import sys
import django
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from django.db import transaction
from inventory.models import Unit, Club, Building, Floor
from bookings.models import Booking, Companion, Contract

def reset_and_import(file_path):
    print("WARNING: Deleting ALL synced data in Django to do a fresh start from Excel...")
    Companion.objects.all().delete()
    Booking.objects.all().delete()
    Contract.objects.all().delete()
    Unit.objects.all().delete()
    Floor.objects.all().delete()
    Building.objects.all().delete()
    Club.objects.all().delete()
    print("Data cleared. Ready to import units.")

    print(f"Reading data from {file_path}")
    df = pd.read_excel(file_path)
    df = df.replace({np.nan: ''})
    
    count = 0
    with transaction.atomic():
        for _, row in df.iterrows():
            try:
                club_name = str(row.get('النادي', '')).strip()
                building_input = str(row.get('رقم العمارة', '')).strip()
                unit_no = str(row.get('رقم الوحدة', '')).strip()
                if not unit_no or unit_no == 'nan':
                    continue
                
                classification = str(row.get('التصنيف', '')).strip()
                unit_type_raw = str(row.get('نوع الوحدة', '')).strip()
                allocation_raw = str(row.get('مخصصات', '')).strip()
                floor_raw = str(row.get('الدور', '')).strip()
                
                # mapping
                unit_type_map = {
                    'شقة 1 غرفة': 'APARTMENT_1B',
                    'شقة 2 غرفة': 'APARTMENT_2B',
                    'شقة 3 غرفة': 'APARTMENT_3B',
                    'غرفة': 'ROOM',
                    'جناح': 'SUITE',
                    'فيلا': 'VILLA',
                }
                unit_type = unit_type_map.get(unit_type_raw, 'APARTMENT_1B')
                
                allocation_map = {
                    'اسكان إداري': 'ADMINISTRATIVE',
                    'سكن إداري': 'ADMINISTRATIVE',
                    'اسكان إدارى': 'ADMINISTRATIVE',
                    'مخصصات القائد': 'COMMANDER',
                    'مخصصات الشركات': 'COMPANY',
                    'اسكان دائم عقود': 'PERMANENT'
                }
                allocation = allocation_map.get(allocation_raw, '')
                
                if not building_input.startswith('عمارة') and building_input != '':
                    building_name = f"عمارة {building_input}"
                else:
                    building_name = building_input
                    
                club, _ = Club.objects.get_or_create(name=club_name, defaults={'city': 'غير محدد'})
                building, _ = Building.objects.get_or_create(club=club, name=building_name)
                
                # Use a default level_number=1, but update the label
                floor, _ = Floor.objects.get_or_create(building=building, level_number=1)
                if floor_raw:
                    floor.label = floor_raw
                    floor.save()
                
                # Check for beds count if suite or 1b vs 2b, default 2 for 1B, 4 for 2B etc
                # Model defaults to capacity=2
                capacity = 2
                if unit_type == 'APARTMENT_2B': capacity = 4
                elif unit_type == 'APARTMENT_3B': capacity = 6
                elif unit_type == 'SUITE': capacity = 4
                
                unit, created = Unit.objects.get_or_create(
                    floor=floor,
                    unit_no=unit_no,
                    defaults={
                        'unit_type': unit_type,
                        'classification': classification,
                        'allocation': allocation,
                        'capacity': capacity
                    }
                )
                
                if not created:
                    unit.classification = classification
                    unit.allocation = allocation
                    unit.unit_type = unit_type
                    unit.capacity = capacity
                    unit.save()
                    
                count += 1
            except Exception as e:
                print(f"Error processing row for {club_name} {unit_no}: {e}")
                
    print(f"Successfully imported {count} units from Excel.")

if __name__ == "__main__":
    file_path = r"d:\housing\Data.xlsx"
    reset_and_import(file_path)
