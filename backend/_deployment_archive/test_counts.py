import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking

print('Total start 2025:', Booking.objects.filter(start_date__year=2025).count())
print('Total record 2025:', Booking.objects.filter(record_date__year=2025).count())
print('Confirmed record 2025:', Booking.objects.filter(record_date__year=2025, status='مؤكد').count())
print('Confirmed start 2025:', Booking.objects.filter(start_date__year=2025, status='مؤكد').count())
print('Draft start 2025:', Booking.objects.filter(start_date__year=2025, status='غير مؤكد').count())
