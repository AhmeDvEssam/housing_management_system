import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from payments.models import Contract
from bookings.models import Booking

contracts = Contract.objects.all()
if contracts.exists():
    print(f"Contract exists: {contracts.first().id}")
else:
    booking = Booking.objects.first()
    if booking:
        contract = Contract.objects.create(booking=booking, contract_no="TEST-001")
        print(f"Created contract: {contract.id}")
    else:
        print("No bookings found to create a contract for.")
