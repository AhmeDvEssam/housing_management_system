from datetime import date

from django.test import TestCase

from bookings.models import Booking, BookingStatus, BookingType
from inventory.models import Building, Club, Floor, Unit, UnitType
from members.models import Member
from .models import Payment, PaymentStatus


class PaymentTests(TestCase):
    def setUp(self) -> None:
        club = Club.objects.create(name="نادي الصفا")
        building = Building.objects.create(club=club, name="عمارة ب")
        floor = Floor.objects.create(building=building, level_number=1)
        unit = Unit.objects.create(
            floor=floor, unit_no="201", unit_type=UnitType.ROOM, capacity=2
        )
        member = Member.objects.create(membership_no="3001", full_name="حسن منصور")
        self.booking = Booking.objects.create(
            member=member,
            unit=unit,
            booking_type=BookingType.LOTTERY,
            status=BookingStatus.PENDING_PAYMENT,
            start_date=date(2026, 7, 1),
            end_date=date(2026, 7, 3),
        )

    def test_payment_confirms_booking(self) -> None:
        payment = Payment.objects.create(
            booking=self.booking,
            amount=500.00,
            status=PaymentStatus.PAID,
        )
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, BookingStatus.CONFIRMED)
        self.assertIsNotNone(payment.paid_at)
