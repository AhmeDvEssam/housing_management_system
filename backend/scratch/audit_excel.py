import sys
import os
import django
import pandas as pd

# Setup Django
sys.path.append(r'd:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Club

def audit():
    df = pd.read_excel(r'd:\housing\Data.xlsx', sheet_name='data')
    df['رقم الوحدة'] = df['رقم الوحدة'].astype(str).str.strip()
    
    print("--- Audit Report ---")
    clubs = df['النادي'].unique()
    for club_name in clubs:
        club_df = df[df['النادي'] == club_name]
        excel_units = set(club_df['رقم الوحدة'].unique())
        
        db_units_qs = Unit.objects.filter(floor__building__club__name=club_name)
        db_units = set(db_units_qs.values_list('unit_no', flat=True))
        
        missing = excel_units - db_units
        extra = db_units - excel_units
        
        excel_alloc_count = len(club_df[club_df['مخصصات'].notna() & (club_df['مخصصات'].astype(str).str.strip() != '')])
        db_alloc_count = db_units_qs.exclude(allocation__isnull=True).exclude(allocation='').count()
        
        print(f"Club: {club_name}")
        print(f"  Units: Excel={len(excel_units)}, DB={len(db_units)}")
        if missing: print(f"  MISSING in DB: {missing}")
        if extra: print(f"  EXTRA in DB: {extra}")
        print(f"  Allocations: Excel={excel_alloc_count}, DB={db_alloc_count}")
        if excel_alloc_count != db_alloc_count:
            print(f"  !!! ALLOCATION MISMATCH !!!")
        print("-" * 20)

if __name__ == '__main__':
    audit()
