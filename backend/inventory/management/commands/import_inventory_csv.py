import csv
from pathlib import Path
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from inventory.models import (
    Club,
    Building,
    BuildingType,
    Floor,
    Unit,
    UnitType,
    Orientation,
)


ARABIC_TRUE = {"نعم", "صحيح", "1", "yes", "true", "y"}
ARABIC_FALSE = {"لا", "خطأ", "0", "no", "false", "n"}

UNIT_TYPE_MAP = {
    "غرفة": UnitType.ROOM,
    "room": UnitType.ROOM,
    "شقة": UnitType.APARTMENT,
    "apartment": UnitType.APARTMENT,
    "جناح": UnitType.SUITE,
    "suite": UnitType.SUITE,
}

ORIENTATION_MAP = {
    "بحري": Orientation.BAHARI,
    "قبلي": Orientation.QIBLI,
    "إطلالة بحر": Orientation.SEA_VIEW,
    "اطلالة بحر": Orientation.SEA_VIEW,
    "sea view": Orientation.SEA_VIEW,
    "إطلالة خلفية": Orientation.BACK_VIEW,
    "اطلالة خلفية": Orientation.BACK_VIEW,
    "back view": Orientation.BACK_VIEW,
}

BUILDING_TYPE_MAP = {
    "مبنى": BuildingType.BUILDING,
    "building": BuildingType.BUILDING,
    "فندق": BuildingType.HOTEL,
    "hotel": BuildingType.HOTEL,
    "أخرى": BuildingType.OTHER,
    "other": BuildingType.OTHER,
}


def normalize(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_bool(value: object, default: bool = False) -> bool:
    text = normalize(value).lower()
    if text in ARABIC_TRUE:
        return True
    if text in ARABIC_FALSE:
        return False
    return default


def first_value(row: dict, keys: Iterable[str], default: str = "") -> str:
    for key in keys:
        if key in row and normalize(row[key]):
            return normalize(row[key])
    return default


class Command(BaseCommand):
    help = "استيراد المخزون (الوحدات) من ملف CSV"

    def add_arguments(self, parser) -> None:
        parser.add_argument("csv_path", type=str, help="مسار ملف CSV")

    def handle(self, *args, **options) -> None:
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError("ملف CSV غير موجود")

        created_units = 0
        updated_units = 0
        errors = 0

        with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            with transaction.atomic():
                for index, row in enumerate(reader, start=2):
                    club_name = first_value(row, ["club_name", "اسم النادي"])
                    building_name = first_value(row, ["building_name", "اسم المبنى"])
                    floor_number = first_value(row, ["floor_number", "رقم الدور"])
                    unit_no = first_value(row, ["unit_no", "رقم الوحدة"])
                    unit_type_raw = first_value(row, ["unit_type", "نوع الوحدة"])
                    capacity_raw = first_value(row, ["capacity", "السعة"])

                    if not all([club_name, building_name, floor_number, unit_no, unit_type_raw, capacity_raw]):
                        errors += 1
                        self.stderr.write(
                            f"سطر {index}: بيانات أساسية مفقودة"
                        )
                        continue

                    city = first_value(row, ["city", "المدينة"], "")
                    building_type_raw = first_value(
                        row, ["building_type", "نوع المبنى"], "مبنى"
                    )
                    floor_label = first_value(row, ["floor_label", "اسم الدور"], "")
                    orientation_raw = first_value(row, ["orientation", "الاتجاه"], "")
                    is_bookable_raw = first_value(row, ["is_bookable", "قابلة للحجز"], "1")
                    is_maintenance_raw = first_value(row, ["is_maintenance", "تحت الصيانة"], "0")
                    notes = first_value(row, ["notes", "ملاحظات"], "")

                    unit_type = UNIT_TYPE_MAP.get(unit_type_raw.lower(), None)
                    if unit_type is None:
                        unit_type = UNIT_TYPE_MAP.get(unit_type_raw, None)
                    if unit_type is None:
                        errors += 1
                        self.stderr.write(f"سطر {index}: نوع وحدة غير معروف")
                        continue

                    orientation = ORIENTATION_MAP.get(orientation_raw.lower(), "")
                    if not orientation and orientation_raw:
                        orientation = ORIENTATION_MAP.get(orientation_raw, "")

                    building_type = BUILDING_TYPE_MAP.get(building_type_raw.lower(), None)
                    if building_type is None:
                        building_type = BUILDING_TYPE_MAP.get(building_type_raw, BuildingType.BUILDING)

                    try:
                        floor_number_int = int(floor_number)
                        capacity = int(capacity_raw)
                    except ValueError:
                        errors += 1
                        self.stderr.write(f"سطر {index}: رقم دور أو سعة غير صالح")
                        continue

                    club, _ = Club.objects.get_or_create(
                        name=club_name, defaults={"city": city}
                    )
                    building, _ = Building.objects.get_or_create(
                        club=club,
                        name=building_name,
                        defaults={"building_type": building_type},
                    )
                    floor, _ = Floor.objects.get_or_create(
                        building=building,
                        level_number=floor_number_int,
                        defaults={"label": floor_label},
                    )

                    unit, created = Unit.objects.update_or_create(
                        floor=floor,
                        unit_no=unit_no,
                        defaults={
                            "unit_type": unit_type,
                            "capacity": capacity,
                            "orientation": orientation,
                            "is_bookable": parse_bool(is_bookable_raw, True),
                            "is_maintenance": parse_bool(is_maintenance_raw, False),
                            "notes": notes,
                        },
                    )
                    if created:
                        created_units += 1
                    else:
                        updated_units += 1

        self.stdout.write(
            f"تم الاستيراد: جديد {created_units}، تحديث {updated_units}، أخطاء {errors}"
        )
