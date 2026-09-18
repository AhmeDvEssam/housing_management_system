"""
سكريبت لإصلاح البيانات الحالية: مزامنة unit.allocation من جدول Allocation
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

import django
django.setup()

from inventory.models import Unit, Allocation

allocations = Allocation.objects.all().select_related('unit')
print(f"عدد المخصصات في جدول Allocation: {allocations.count()}")

updated = 0
for alloc in allocations:
    unit = alloc.unit
    if unit.allocation != alloc.allocation_type:
        old_val = unit.allocation
        unit.allocation = alloc.allocation_type
        unit.save(update_fields=['allocation'])
        updated += 1
        print(f"  ✓ وحدة {unit.unit_no}: '{old_val}' → '{alloc.allocation_type}'")

print(f"\nتم تحديث {updated} وحدة من أصل {allocations.count()} مخصص.")

# التحقق
units_with_alloc = Unit.objects.exclude(allocation__isnull=True).exclude(allocation='')
print(f"\nالوحدات التي لديها allocation الآن: {units_with_alloc.count()}")
