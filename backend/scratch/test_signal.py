"""اختبار أن الـ Signal شغال"""
import os, sys, io, django
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit, Allocation

# اختار وحدة بدون مخصصات
unit = Unit.objects.filter(allocation__isnull=True).first() or Unit.objects.filter(allocation='').first()
print(f'وحدة تجريبية: {unit.unit_no} | allocation قبل: "{unit.allocation}"')

# أنشئ مخصص
a = Allocation.objects.create(unit=unit, allocation_type='COMMANDER', allocated_to='تجربة signal')
unit.refresh_from_db()
print(f'بعد الإنشاء: allocation = "{unit.allocation}"')
assert unit.allocation == 'COMMANDER', 'FAIL: signal لم يعمل عند الإنشاء!'

# احذف المخصص
a.delete()
unit.refresh_from_db()
print(f'بعد الحذف: allocation = "{unit.allocation}"')
assert not unit.allocation or unit.allocation == 'None', 'FAIL: signal لم يعمل عند الحذف!'

print('✅ الـ Signal شغال تمام! أي مخصص تضيفه أو تحذفه هيتزامن تلقائياً')
