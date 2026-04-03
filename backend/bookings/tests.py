from datetime import date

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from inventory.models import Building, Club, Floor, Unit, UnitType
from members.models import Member
from .models import Booking, BookingDay, BookingStatus, BookingType


class BookingModelTests(TestCase):
    def setUp(self) -> None:
        self.club = Club.objects.create(name="نادي النيل")
        self.building = Building.objects.create(club=self.club, name="عمارة أ")
        self.floor = Floor.objects.create(building=self.building, level_number=1)
        self.unit = Unit.objects.create(
            floor=self.floor, unit_no="101", unit_type=UnitType.ROOM, capacity=2
        )
        self.member = Member.objects.create(
            membership_no="2001", full_name="أحمد سالم"
        )
        self.client = APIClient()

    def test_date_validation(self) -> None:
        booking = Booking(
            member=self.member,
            unit=self.unit,
            start_date=date(2026, 6, 5),
            end_date=date(2026, 6, 5),
        )
        with self.assertRaises(ValidationError):
            booking.save()

    def test_booking_days_created_on_confirmed(self) -> None:
        booking = Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.CONFIRMED,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 4),
        )
        self.assertEqual(BookingDay.objects.filter(booking=booking).count(), 3)

    def test_booking_days_not_created_on_draft(self) -> None:
        booking = Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.DRAFT,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
        )
        self.assertEqual(BookingDay.objects.filter(booking=booking).count(), 0)

    def test_booking_days_created_on_pending_payment(self) -> None:
        booking = Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.PENDING_PAYMENT,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
        )
        self.assertEqual(BookingDay.objects.filter(booking=booking).count(), 2)

    def test_conflict_prevention(self) -> None:
        Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.CONFIRMED,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 4),
        )
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                member=self.member,
                unit=self.unit,
                status=BookingStatus.CONFIRMED,
                start_date=date(2026, 6, 3),
                end_date=date(2026, 6, 5),
            )

    def test_conflict_prevention_with_pending_payment(self) -> None:
        Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.PENDING_PAYMENT,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 4),
        )
        with self.assertRaises(ValidationError):
            Booking.objects.create(
                member=self.member,
                unit=self.unit,
                status=BookingStatus.CONFIRMED,
                start_date=date(2026, 6, 2),
                end_date=date(2026, 6, 5),
            )

    def test_booking_days_deleted_on_cancel(self) -> None:
        booking = Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.CONFIRMED,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
        )
        self.assertEqual(BookingDay.objects.filter(booking=booking).count(), 2)
        booking.status = BookingStatus.CANCELLED
        booking.save()
        self.assertEqual(BookingDay.objects.filter(booking=booking).count(), 0)

    def test_invalid_status_transition(self) -> None:
        booking = Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.DRAFT,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 3),
        )
        booking.status = BookingStatus.CHECKED_IN
        with self.assertRaises(ValidationError):
            booking.save()

    def test_lottery_defaults(self) -> None:
        booking = Booking.objects.create(
            member=self.member,
            unit=self.unit,
            booking_type=BookingType.LOTTERY,
            start_date=date(2026, 6, 20),
            end_date=date(2026, 6, 22),
        )
        self.assertEqual(booking.status, BookingStatus.PENDING_PAYMENT)
        self.assertEqual(booking.payment_deadline, date(2026, 6, 6))

    def test_expire_lottery_bookings_command(self) -> None:
        booking = Booking.objects.create(
            member=self.member,
            unit=self.unit,
            booking_type=BookingType.LOTTERY,
            status=BookingStatus.PENDING_PAYMENT,
            start_date=date(2026, 6, 20),
            end_date=date(2026, 6, 22),
            payment_deadline=date(2026, 5, 1),
        )
        call_command("expire_lottery_bookings")
        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.EXPIRED)

    def test_conflict_api_with_pending_payment(self) -> None:
        Booking.objects.create(
            member=self.member,
            unit=self.unit,
            status=BookingStatus.PENDING_PAYMENT,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 4),
        )
        response = self.client.get(
            "/api/bookings/conflicts",
            {
                "unit_id": self.unit.id,
                "start_date": "01-06-2026",
                "end_date": "03-06-2026",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["has_conflict"])
        self.assertTrue(len(data["conflict_days"]) > 0)
