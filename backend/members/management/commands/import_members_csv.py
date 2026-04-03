import csv
from pathlib import Path
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from members.models import Member


ARABIC_TRUE = {"نعم", "صحيح", "1", "yes", "true", "y"}
ARABIC_FALSE = {"لا", "خطأ", "0", "no", "false", "n"}


def normalize(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def parse_bool(value: object, default: bool = True) -> bool:
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
    help = "استيراد الأعضاء من ملف CSV"

    def add_arguments(self, parser) -> None:
        parser.add_argument("csv_path", type=str, help="مسار ملف CSV")

    def handle(self, *args, **options) -> None:
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError("ملف CSV غير موجود")

        created_members = 0
        updated_members = 0
        errors = 0

        with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            with transaction.atomic():
                for index, row in enumerate(reader, start=2):
                    membership_no = first_value(
                        row, ["membership_no", "رقم العضوية"]
                    )
                    full_name = first_value(row, ["full_name", "اسم العضو"])

                    if not membership_no or not full_name:
                        errors += 1
                        self.stderr.write(
                            f"سطر {index}: رقم العضوية أو الاسم غير موجود"
                        )
                        continue

                    phone = first_value(row, ["phone", "رقم الهاتف"], "")
                    email = first_value(row, ["email", "البريد الإلكتروني"], "")
                    national_id = first_value(row, ["national_id", "الرقم القومي"], "")
                    address = first_value(row, ["address", "العنوان"], "")
                    notes = first_value(row, ["notes", "ملاحظات"], "")
                    is_active_raw = first_value(row, ["is_active", "نشط"], "1")

                    member, created = Member.objects.update_or_create(
                        membership_no=membership_no,
                        defaults={
                            "full_name": full_name,
                            "phone": phone,
                            "email": email,
                            "national_id": national_id,
                            "address": address,
                            "notes": notes,
                            "is_active": parse_bool(is_active_raw, True),
                        },
                    )
                    if created:
                        created_members += 1
                    else:
                        updated_members += 1

        self.stdout.write(
            f"تم الاستيراد: جديد {created_members}، تحديث {updated_members}، أخطاء {errors}"
        )
