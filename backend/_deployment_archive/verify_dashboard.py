import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
sys.path.append('backend')
django.setup()

from bookings.models import Booking
from django.db.models import Sum

# Verified counts for 2025
b_2025 = Booking.objects.filter(record_date__year=2025, status='مؤكد')

count = b_2025.count()
revenue = b_2025.aggregate(total=Sum('total_price'))['total']

# Print breakdown by pay_method
bank = b_2025.filter(pay_method=2).aggregate(total=Sum('total_price'))['total']
visa = b_2025.filter(pay_method=1).aggregate(total=Sum('total_price'))['total']
unpaid = b_2025.filter(pay_method=0).aggregate(total=Sum('total_price'))['total']

print(f"Total Confirmed Bookings (2025): {count}")
print(f"Total Revenue (2025): {revenue}")
print(f"Bank Transfer (2025): {bank}")
print(f"Visa (2025): {visa}")
print(f"Unpaid (2025): {unpaid}")
