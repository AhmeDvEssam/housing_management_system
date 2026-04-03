from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from bookings.models import Booking, BookingStatus, BookingType
from inventory.models import Building, Club, Floor, Unit, UnitType
from members.models import Member


class WallboardApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        club = Club.objects.create(name="نادي الزهور")
        building = Building.objects.create(club=club, name="عمارة ج")
        floor = Floor.objects.create(building=building, level_number=1)
        self.unit = Unit.objects.create(
            floor=floor, unit_no="301", unit_type=UnitType.ROOM, capacity=2
        )
        member = Member.objects.create(membership_no="4001", full_name="سمر خالد")
        Booking.objects.create(
            member=member,
            unit=self.unit,
            booking_type=BookingType.LOTTERY,
            status=BookingStatus.PENDING_PAYMENT,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3),
        )

    def test_wallboard_returns_lottery_pending_status(self) -> None:
        response = self.client.get(
            "/api/dashboard/wallboard",
            {"date": "01-08-2026", "days": 2},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["units"]), 1)
        status = data["units"][0]["statuses"][0]["status"]
        self.assertEqual(status, "LOTTERY_PENDING")

    def test_units_status_endpoint(self) -> None:
        response = self.client.get(
            "/api/units/status",
            {"date": "01-08-2026"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["units"]), 1)
        self.assertEqual(data["units"][0]["status"], "LOTTERY_PENDING")
