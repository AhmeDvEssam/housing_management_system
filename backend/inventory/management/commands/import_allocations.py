import os
import re
from django.core.management.base import BaseCommand
from inventory.models import Club, Unit, Allocation, AllocationType

class Command(BaseCommand):
    help = "Import allocations from the extracted text file"

    def handle(self, *args, **options):
        file_path = "allocations_text.txt"
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Split by clubs (heuristic)
        clubs_sections = {
            "رأس البر": ["213", "214", "215", "122", "102", "212", "124", "322", "323", "324", "522", "523", "524", "525", "422", "312", "412", "413", "414", "712", "713", "1012", "113", "114", "115", "801", "821", "806", "812", "813", "912", "123", "124", "125", "526", "921"],
            "جمصة": ["13/1", "14/1", "23/1", "27/1", "4/1", "18/1", "33/1", "12/2", "21/2", "36/2", "5/2", "33/2"],
            "بورسعيد": ["403", "404", "504", "603", "503", "505", "506", "604", "602", "405", "406", "407"],
            "فايد": ["213", "214", "323", "324", "313", "314", "315", "223", "224", "222", "114", "123"],
            "الأنفوشي": ["602", "302", "102", "604", "304", "407", "809", "707", "404", "807", "702", "806", "205", "505", "705", "401", "703", "804", "803"]
        }

        # Clear existing allocations to avoid duplicates if re-running
        # Allocation.objects.all().delete()

        for club_name, unit_list in clubs_sections.items():
            club = Club.objects.filter(name__icontains=club_name).first()
            if not club:
                self.stdout.write(self.style.WARNING(f"Club {club_name} not found in DB"))
                continue

            created_count = 0
            for u_no in unit_list:
                # Try to find the unit in this club
                # Strip leading zeros or handle different formats
                unit = Unit.objects.filter(floor__building__club=club, unit_no=u_no).first()
                if not unit:
                    # Try fuzzy match (e.g. 13/1 vs 131)
                    clean_no = u_no.replace("/", "")
                    unit = Unit.objects.filter(floor__building__club=club, unit_no=clean_no).first()
                
                if unit:
                    # Create allocation
                    Allocation.objects.get_or_create(
                        unit=unit,
                        allocation_type=AllocationType.CLUB,
                        defaults={
                            "allocated_to": "مخصصات النادي (مستوردة)",
                            "notes": "تم الاستيراد آلياً من ملف مخصصات النوادى"
                        }
                    )
                    created_count += 1
            
            self.stdout.write(self.style.SUCCESS(f"Created {created_count} allocations for {club_name}"))
