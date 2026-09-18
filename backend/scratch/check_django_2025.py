import os
import django
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r'D:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

total_2025 = Booking.objects.filter(record_date__year=2025, status='مؤكد').count()
print(f"Total in Django for 2025 (status=مؤكد): {total_2025}")

from django.db.models import Q
from_member_contract = Booking.objects.filter(record_date__year=2025, status='مؤكد', contract_no__isnull=False).exclude(contract_no="").count()
print(f"From MEMBER_CONTRACT (has contract_no): {from_member_contract}")

from_person_booked = Booking.objects.filter(record_date__year=2025, status='مؤكد').filter(Q(contract_no="") | Q(contract_no__isnull=True)).count()
print(f"From PERSON_BOOKED (no contract_no): {from_person_booked}")
