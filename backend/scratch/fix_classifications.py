"""تحديث التصنيفات من Data.xlsx للوحدات الموجودة"""
import os, sys, io, django
import pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit

file_path = r"d:\housing\Data.xlsx"
df = pd.read_excel(file_path)

updated = 0
not_found = 0
already_ok = 0

for _, row in df.iterrows():
    club_name = str(row.get('النادي', '')).strip()
    building_input = str(row.get('رقم العمارة', '')).strip()
    unit_no = str(row.get('رقم الوحدة', '')).strip()
    classification = str(row.get('التصنيف', '')).strip()

    if not unit_no or unit_no == 'nan' or not classification or classification == 'nan':
        continue

    unit = Unit.objects.filter(
        unit_no=unit_no,
        floor__building__name__icontains=building_input,
        floor__building__club__name=club_name
    ).first()

    if unit:
        if unit.classification != classification:
            old = unit.classification
            unit.classification = classification
            unit.save(update_fields=['classification'])
            updated += 1
            if updated <= 10:
                print(f'  ✓ {unit_no} ({building_input}): "{old}" → "{classification}"')
        else:
            already_ok += 1
    else:
        not_found += 1
        if not_found <= 5:
            print(f'  ✗ لم يتم العثور على: {unit_no} في {building_input} / {club_name}')

if updated > 10:
    print(f'  ... و {updated - 10} وحدة أخرى')

print(f'\n=== النتيجة ===')
print(f'تم تحديث: {updated}')
print(f'تصنيف سليم بالفعل: {already_ok}')
print(f'لم يتم العثور عليها: {not_found}')

# Verify
from collections import Counter
vals = list(Unit.objects.values_list('classification', flat=True))
c = Counter(vals)
print(f'\n=== توزيع التصنيفات بعد التحديث ===')
for k, v in c.most_common():
    print(f'  {k or "(فارغ)"}: {v}')
