import sys, io, os, django
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from bookings.models import LotteryResult, Booking, BookingType
from inventory.models import Club

# The key question: HOW did 172 bookings get tagged as LOTTERY?
# In smart_sync.py, a booking is tagged LOTTERY if:
#   LotteryResult.objects.filter(membership_no=str(mem_no), unit_no=str(flat_num)).exists()
# 
# So the sync checks if this member+unit combo exists in LotteryResult.
# The LotteryResult table has 1333 entries loaded from the Excel.
# 172 of those member+unit combos were found in the Oracle DMP contracts/bookings.
# That means 172 members who won the lottery also had existing contracts in the DMP!

# Let's verify: are these REAL lottery matches or false positives?
print("=== Verifying the 172 lottery-tagged bookings ===")
lottery_bk = Booking.objects.filter(booking_type=BookingType.LOTTERY).select_related('member', 'unit')

# Check a sample match
for b in lottery_bk[:5]:
    if b.member:
        lr_matches = LotteryResult.objects.filter(membership_no=b.member.membership_no)
        unit_str = str(b.unit.unit_no) if b.unit else ''
        print(f"\n  Booking: mem={b.member.membership_no}, unit_no={b.unit.unit_no}, unit_club={b.unit.floor.building.club.name if b.unit else 'N/A'}")
        print(f"  Dates: {b.start_date} -> {b.end_date}")
        for lr in lr_matches:
            print(f"    LotteryResult: club={lr.club_name}, unit_no={lr.unit_no}, period={lr.period_no}")
            print(f"    Match unit? {lr.unit_no == unit_str}")

# The REAL question: the DMP has contracts from previous years. The lottery is for 2026.
# If a member won the 2026 lottery AND also had old contracts from past years,
# the sync incorrectly tags those OLD contracts as lottery bookings.
print("\n\n=== Year distribution of lottery-tagged bookings ===")
from collections import Counter
years = Counter()
for b in lottery_bk:
    years[b.start_date.year] += 1
for y, c in sorted(years.items()):
    print(f"  Year {y}: {c} bookings")

# Check if any of the 1333 LotteryResult entries match actual DMP data for the CORRECT period
print("\n\n=== LotteryResult period distribution ===")
periods = Counter()
for lr in LotteryResult.objects.all():
    periods[lr.period_no] += 1
for p, c in sorted(periods.items()):
    print(f"  Period {p}: {c} entries")
