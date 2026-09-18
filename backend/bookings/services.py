import logging
from django.db import transaction
from django.utils import timezone
from members.models import Member
from inventory.models import Unit, Period
from bookings.models import Booking, BookingType, LotteryResult, PersonTypeChoices

logger = logging.getLogger(__name__)

LOTTERY_CLUB_MAP = {
    'نادى 6 اكتوبر الانفوشى': 'فندق الانفوشي',
    'نادى 6 اكتوبر بورسعيد': 'نادي بورسعيد',
    'نادى 6 اكتوبر رأس البر': 'نادي راس البر',
    'نادى 6 اكتوبر فايـــد': 'نادي فايد',
    'نادى 6 اكتوبر جمصــــه': 'نادي جمصة',
}

CIVILIAN_RANKS = ['19', '20', '21']

def sync_lottery_results_to_bookings():
    """
    Synchronizes LotteryResult entries to actual Booking records.
    
    Correct logic:
    1. For each LotteryResult, find the member, the won unit, and the period.
    2. Check if there's ALREADY a booking for this member on this EXACT unit in this period:
       - If YES -> just tag it as LOTTERY, keep its status (paid/unpaid).
    3. If no exact match, check if member has a booking on a DIFFERENT unit in same period:
       - If YES -> update that booking's unit to the lottery-won unit, tag as LOTTERY.
    4. If no booking exists at all for this member in this period:
       - Create a new LOTTERY booking (unpaid).
       - If the won unit has a conflicting booking by another member, skip with warning.
    """
    results = LotteryResult.objects.all()
    total_count = results.count()
    
    matched_exact = 0       # Had booking on same unit already
    matched_moved = 0       # Had booking on different unit, moved to lottery unit
    created_new = 0         # No booking existed, created new
    conflicts_count = 0     # Unit occupied by someone else AND member had no booking
    errors = 0
    unmatched_units = []
    
    with transaction.atomic():
        # Step 1: We no longer reset LOTTERY to STANDARD because all 2026 bookings MUST be LOTTERY.
        # reset_count = Booking.objects.filter(booking_type=BookingType.LOTTERY).update(
        #     booking_type=BookingType.STANDARD
        # )
        # print(f"[INFO] Reset {reset_count} existing lottery bookings back to STANDARD for clean recalculation.")
        print("[INFO] Retaining all 2026 LOTTERY tags as requested by the user.")
        
        for lr in results:
            django_club = LOTTERY_CLUB_MAP.get(lr.club_name.strip())
            if not django_club:
                unmatched_units.append(f"Club='{lr.club_name}' Unit='{lr.unit_no}' (unmatched club)")
                errors += 1
                continue
                
            unit = Unit.objects.filter(floor__building__club__name=django_club, unit_no=lr.unit_no).first()
            if not unit:
                unmatched_units.append(f"Club='{lr.club_name}' Unit='{lr.unit_no}' (unmatched unit)")
                errors += 1
                continue
                
            period = Period.objects.filter(id=lr.period_no).first()
            if not period:
                errors += 1
                continue
                
            member = Member.objects.filter(membership_no=lr.membership_no).first()
            if not member:
                errors += 1
                continue
            
            # Determine person type
            if member.rank in ['مدنى', 'مدنية', 'مدني*']:
                person_type = PersonTypeChoices.FAMILY_MEMBER
            else:
                person_type = PersonTypeChoices.MILITARY
            
            from django.db.models import Q
            
            # Case A: Check if member already has a booking on THIS EXACT unit in this period
            exact_booking = Booking.objects.filter(
                Q(member=member) | Q(guest_id_no=member.membership_no),
                unit=unit,
                start_date__lte=period.end_date,
                end_date__gte=period.start_date
            ).first()
            
            if exact_booking:
                # Perfect match - just tag as LOTTERY, preserve status
                Booking.objects.filter(pk=exact_booking.pk).update(
                    booking_type=BookingType.LOTTERY,
                    person_type=person_type
                )
                matched_exact += 1
                continue
            
            # Case B: Member has booking on a DIFFERENT unit in this period
            other_unit_booking = Booking.objects.filter(
                Q(member=member) | Q(guest_id_no=member.membership_no),
                start_date__lte=period.end_date,
                end_date__gte=period.start_date
            ).first()
            
            if other_unit_booking:
                # Member has a contract booking on different unit - tag as LOTTERY
                # Don't move unit (the contract sync put them on the correct unit from Oracle)
                Booking.objects.filter(pk=other_unit_booking.pk).update(
                    booking_type=BookingType.LOTTERY,
                    person_type=person_type
                )
                matched_moved += 1
                continue
            
            # Case C: No booking at all for this member in this period -> create new
            # But first check if the won unit is occupied by someone else
            conflicting = Booking.objects.filter(
                unit=unit,
                start_date__lte=period.end_date,
                end_date__gte=period.start_date
            ).first()
            
            if conflicting:
                conflicts_count += 1
                continue
            
            # Create new lottery booking
            try:
                Booking.objects.create(
                    member=member,
                    unit=unit,
                    start_date=period.start_date,
                    end_date=period.end_date,
                    guest_name=member.full_name,
                    guest_id_no=member.membership_no,
                    status='غير مؤكد',
                    booking_type=BookingType.LOTTERY,
                    person_type=person_type,
                    notes=""
                )
                created_new += 1
            except Exception as e:
                errors += 1
                continue
                
    total_lottery = matched_exact + matched_moved + created_new
    print(f"[SUCCESS] Lottery Sync complete:")
    print(f"  - Total LotteryResult processed: {total_count}")
    print(f"  - Matched (exact unit): {matched_exact}")
    print(f"  - Matched (different unit): {matched_moved}")
    print(f"  - Created new (unpaid): {created_new}")
    print(f"  - Total tagged as LOTTERY: {total_lottery}")
    print(f"  - Conflicts (unit occupied, no member booking): {conflicts_count}")
    print(f"  - Errors/Unmatched: {errors}")
    if unmatched_units:
        print("  - Unmatched details:")
        for uu in set(unmatched_units):
            print(f"      * {uu}")
            
    return total_count, total_lottery, created_new, errors
