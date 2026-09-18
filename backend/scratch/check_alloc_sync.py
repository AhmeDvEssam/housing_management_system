"""تحقق: مقارنة Allocation records مع unit.allocation"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
import django; django.setup()

from inventory.models import Unit, Allocation, AllocationType

alloc_records = Allocation.objects.all().select_related('unit')
units_with_field = Unit.objects.exclude(allocation__isnull=True).exclude(allocation='')

print(f"سجلات جدول Allocation: {alloc_records.count()}")
print(f"وحدات بحقل unit.allocation مملوء: {units_with_field.count()}")

# Find units that have Allocation records but empty unit.allocation
print("\n=== وحدات لها مخصصات في Allocation لكن حقل unit.allocation فاضي ===")
missing = []
for a in alloc_records:
    if not a.unit.allocation:
        missing.append(a)
        print(f"  ❌ ID={a.id} | وحدة {a.unit.unit_no} ({a.unit.floor.building.name}) | نوع: {a.get_allocation_type_display()} | مخصص لـ: {a.allocated_to}")

print(f"\nعدد المخصصات الغير متزامنة: {len(missing)}")

# Also check unique units with allocations
unique_units_in_alloc = set(alloc_records.values_list('unit_id', flat=True))
print(f"\nعدد الوحدات الفريدة في جدول Allocation: {len(unique_units_in_alloc)}")
