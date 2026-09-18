import sys
import io
import os
import django

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(r"d:\housing\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import Booking, BookingType, LotteryResult
from inventory.models import Period
from members.models import Member
from django.db.models import Count

# 1. Duplicate/empty membership numbers in Member table
dupes = Member.objects.values('membership_no').annotate(count=Count('id')).filter(count__gt=1)[:10]
print('Duplicate membership numbers in Member table:', list(dupes))
empty_mem_count = Member.objects.filter(membership_no='').count()
print('Empty membership_no count in Member:', empty_mem_count)

# 2. Check LotteryResult table counts and values
print('\nLotteryResult count:', LotteryResult.objects.count())
lr_empty = LotteryResult.objects.filter(membership_no='').count()
print('Empty membership_no in LotteryResult:', lr_empty)

# Let's inspect some of the matched lottery bookings in our database
matched_lottery_bookings = Booking.objects.filter(booking_type=BookingType.LOTTERY, status='مؤكد')[:15]
print('\nMatched lottery bookings samples:')
for b in matched_lottery_bookings:
    mem_no = b.member.membership_no if b.member else "None"
    print(f"  - Member No: {mem_no} | Guest Name: {b.guest_name} | Unit: {b.unit.unit_no} in {b.unit.floor.building.club.name} | Dates: {b.start_date} to {b.end_date}")
