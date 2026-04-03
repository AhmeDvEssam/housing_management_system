from django.db import IntegrityError
from django.test import TestCase
from .models import Club, Building, Floor, Unit, UnitType


class InventoryModelTests(TestCase):
    def setUp(self) -> None:
        self.club = Club.objects.create(name="نادي الشمس")
        self.building = Building.objects.create(club=self.club, name="عمارة 1")
        self.floor = Floor.objects.create(building=self.building, level_number=1)

    def test_club_unique_name(self) -> None:
        with self.assertRaises(IntegrityError):
            Club.objects.create(name="نادي الشمس")

    def test_unit_unique_per_floor(self) -> None:
        Unit.objects.create(
            floor=self.floor,
            unit_no="101",
            unit_type=UnitType.ROOM,
            capacity=2,
        )
        with self.assertRaises(IntegrityError):
            Unit.objects.create(
                floor=self.floor,
                unit_no="101",
                unit_type=UnitType.ROOM,
                capacity=2,
            )

    def test_unit_str(self) -> None:
        unit = Unit.objects.create(
            floor=self.floor,
            unit_no="102",
            unit_type=UnitType.APARTMENT,
            capacity=4,
        )
        self.assertIn("102", str(unit))
