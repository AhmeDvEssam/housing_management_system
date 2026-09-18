"""فحص أنواع الوحدات في الإكسل مقابل قاعدة البيانات وتصحيحها"""
import os, sys, io, django
import pandas as pd
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit

file_path = r"d:\housing\Data.xlsx"
df = pd.read_excel(file_path)

unit_type_map = {
    'شقة 1 غرفة': 'APARTMENT_1B',
    'شقة 2 غرفة': 'APARTMENT_2B',
    'شقة 3 غرفة': 'APARTMENT_3B',
    'شقة 1': 'APARTMENT_1B',
    'شقة 2': 'APARTMENT_2B',
    'شقة 3': 'APARTMENT_3B',
    'شقة': 'APARTMENT_2B', # Default if just 'شقة'
    'غرفة': 'ROOM',
    'غرفه': 'ROOM',
    'جناح': 'SUITE',
    'فيلا': 'VILLA',
}

def get_capacity(utype):
    if utype == 'APARTMENT_1B': return 2
    if utype == 'APARTMENT_2B': return 4
    if utype == 'APARTMENT_3B': return 6
    if utype == 'SUITE': return 4
    if utype == 'ROOM': return 2
    if utype == 'VILLA': return 6
    return 2

updated_count = 0
unmapped_types = set()

for _, row in df.iterrows():
    club_name = str(row.get('النادي', '')).strip()
    building_input = str(row.get('رقم العمارة', '')).strip()
    unit_no = str(row.get('رقم الوحدة', '')).strip()
    
    # Clean up the unit type raw value
    unit_type_raw = str(row.get('نوع الوحدة', '')).strip()
    
    if not unit_no or unit_no == 'nan':
        continue

    # Try to find mapping
    mapped_type = None
    for k, v in unit_type_map.items():
        if k in unit_type_raw:  # Using 'in' to handle 'غرفة مزدوجة' etc if present
            mapped_type = v
            break
            
    if not mapped_type:
        mapped_type = 'APARTMENT_1B' # Final fallback
        unmapped_types.add(unit_type_raw)

    capacity = get_capacity(mapped_type)

    unit = Unit.objects.filter(
        unit_no=unit_no,
        floor__building__name__icontains=building_input,
        floor__building__club__name=club_name
    ).first()

    if unit:
        changed = False
        if unit.unit_type != mapped_type:
            unit.unit_type = mapped_type
            changed = True
        if unit.capacity != capacity:
            unit.capacity = capacity
            changed = True
            
        if changed:
            unit.save(update_fields=['unit_type', 'capacity'])
            updated_count += 1

print(f"تم تصحيح نوع الوحدة لـ {updated_count} وحدة.")
print(f"أنواع غير معروفة في الإكسل (Unmapped): {unmapped_types}")

# Print current summary from DB
print("\n=== توزيع أنواع الوحدات في قاعدة البيانات حالياً ===")
vals = list(Unit.objects.values_list('unit_type', flat=True))
c = Counter(vals)
for k, v in c.most_common():
    print(f"  {k}: {v}")
