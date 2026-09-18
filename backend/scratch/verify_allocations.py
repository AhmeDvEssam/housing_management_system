"""تحقق نهائي: محاكاة ما يفعله الداشبورد"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
import django; django.setup()

from inventory.models import Unit, Allocation, AllocationType
from datetime import date

print("=== تحقق من الداشبورد ===")
total = Unit.objects.count()
with_alloc = Unit.objects.exclude(allocation__isnull=True).exclude(allocation='').count()
print(f"إجمالي الوحدات: {total}")
print(f"وحدات بمخصصات: {with_alloc}")
print()

# محاكاة KPIs
alloc_types = Unit.objects.exclude(allocation__isnull=True).exclude(allocation='').values_list('allocation', flat=True)
from collections import Counter
counts = Counter(alloc_types)
print("توزيع المخصصات:")
for alloc_type, count in counts.items():
    label = dict(AllocationType.choices).get(alloc_type, alloc_type)
    print(f"  {label}: {count}")

print()
print(f"KPI alloc_total المتوقع: {with_alloc}")
print("✅ الداشبورد المفروض يظهر المخصصات الآن!")
