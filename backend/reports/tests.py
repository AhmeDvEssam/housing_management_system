from datetime import date
from io import BytesIO

from django.test import TestCase
from rest_framework.test import APIClient
from openpyxl import load_workbook

from bookings.models import Booking, BookingStatus
from inventory.models import Building, Club, Floor, Unit, UnitType
from members.models import Member


class ReportsApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        club = Club.objects.create(name="نادي النخيل")
        building = Building.objects.create(club=club, name="عمارة د")
        floor = Floor.objects.create(building=building, level_number=1)
        self.unit_a = Unit.objects.create(
            floor=floor, unit_no="401", unit_type=UnitType.ROOM, capacity=2
        )
        self.unit_b = Unit.objects.create(
            floor=floor,
            unit_no="402",
            unit_type=UnitType.APARTMENT,
            capacity=4,
            is_maintenance=True,
        )
        self.unit_c = Unit.objects.create(
            floor=floor, unit_no="403", unit_type=UnitType.ROOM, capacity=2
        )
        member = Member.objects.create(membership_no="5001", full_name="هدى خالد")
        Booking.objects.create(
            member=member,
            unit=self.unit_a,
            status=BookingStatus.CONFIRMED,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 3),
        )

    def test_occupancy_report(self) -> None:
        response = self.client.get(
            "/api/reports/occupancy",
            {"start_date": "01-09-2026", "end_date": "04-09-2026"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_unit_days"], 6)
        self.assertEqual(data["booked_unit_days"], 2)
        self.assertAlmostEqual(data["occupancy_percent"], 33.33, places=2)

    def test_occupancy_report_xlsx(self) -> None:
        response = self.client.get(
            "/api/reports/occupancy",
            {
                "start_date": "01-09-2026",
                "end_date": "04-09-2026",
                "format": "xlsx",
            },
        )
        self.assertEqual(response.status_code, 200)
        workbook = load_workbook(BytesIO(response.content))
        self.assertEqual(workbook.active.title, "نسبة الإشغال")

    def test_available_units_report(self) -> None:
        response = self.client.get(
            "/api/reports/available",
            {"start_date": "01-09-2026", "end_date": "04-09-2026"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_available"], 1)
        self.assertEqual(data["units"][0]["unit_no"], self.unit_c.unit_no)

    def test_occupied_units_report(self) -> None:
        response = self.client.get(
            "/api/reports/occupied",
            {"start_date": "01-09-2026", "end_date": "04-09-2026"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_bookings"], 1)
        self.assertEqual(data["bookings"][0]["unit_no"], self.unit_a.unit_no)
