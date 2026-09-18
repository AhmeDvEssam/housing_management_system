from django.core.management.base import BaseCommand
import openpyxl
import re
from inventory.models import Club, Building, PricingRule, UnitType

class Command(BaseCommand):
    help = 'Import prices from Excel file into PricingRule'

    def handle(self, *args, **kwargs):
        file_path = r"d:\housing\الاسعار.xlsx"
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to open Excel file: {e}'))
            return

        PricingRule.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Cleared old Pricing Rules"))

        current_club = None
        current_building_group_str = ""

        for row in sheet.iter_rows(min_row=4, values_only=True):
            cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
            if not any(cleaned_row):
                continue
            
            club_str = cleaned_row[2]
            building_group_str = cleaned_row[3]
            unit_desc = cleaned_row[4]

            if not unit_desc and not any(cleaned_row[5:]):
                continue

            if club_str:
                club_name = club_str.replace("نادى", "").strip()
                current_club, _ = Club.objects.get_or_create(name=club_name)

            if building_group_str:
                current_building_group_str = building_group_str

            if not unit_desc:
                continue

            u_type = UnitType.APARTMENT_1B
            if "جناح" in unit_desc:
                u_type = UnitType.SUITE
            elif "غرفة" in unit_desc or "غرفه" in unit_desc:
                if "شقة" not in unit_desc:
                    u_type = UnitType.ROOM

            def safe_decimal(val):
                try:
                    if not val: return 0
                    return round(float(val), 2)
                except:
                    return 0

            rule = PricingRule.objects.create(
                club=current_club,
                unit_type=u_type,
                classification="مكيف" if "مكيف" in unit_desc else ("مميز" if "مميز" in unit_desc else "عادي"),
                view_type="بحرى" if "بحرى" in unit_desc else ("قبلى" if "قبلى" in unit_desc else ""),
                
                price_military=safe_decimal(cleaned_row[5]),
                price_family=safe_decimal(cleaned_row[6]),
                price_civilian_af=safe_decimal(cleaned_row[7]),
                price_civilian_gen_normal=safe_decimal(cleaned_row[8]),
                price_civilian_gen_peak=safe_decimal(cleaned_row[9]),
                
                price_military_50=safe_decimal(cleaned_row[10]) if len(cleaned_row) > 10 else 0,
                price_family_50=safe_decimal(cleaned_row[11]) if len(cleaned_row) > 11 else 0,
                price_civilian_af_50=safe_decimal(cleaned_row[12]) if len(cleaned_row) > 12 else 0,
                price_civilian_gen_normal_50=safe_decimal(cleaned_row[13]) if len(cleaned_row) > 13 else 0,
                price_civilian_gen_peak_50=safe_decimal(cleaned_row[14]) if len(cleaned_row) > 14 else 0,
            )

            # Try to match buildings by numbers
            if current_building_group_str and current_club:
                numbers = re.findall(r'\d+', current_building_group_str)
                if numbers:
                    for num in numbers:
                        b = Building.objects.filter(club=current_club, name__contains=num).first()
                        if b:
                            rule.buildings.add(b)
                elif "الانفوشى" in current_club.name:
                    # In Anfoushy, maybe it applies to all or no specific buildings
                    pass

        count = PricingRule.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} Pricing Rules'))
