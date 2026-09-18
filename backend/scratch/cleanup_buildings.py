import os
import sys
import django

# Setup Django
sys.path.append(r'd:\housing\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club, Building, Floor, Unit

def cleanup_duplicate_buildings():
    print("--- Starting Robust Building Cleanup ---")
    clubs = Club.objects.all()
    for club in clubs:
        buildings = list(Building.objects.filter(club=club))
        # Group by normalized name
        groups = {}
        for b in buildings:
            norm = " ".join(str(b.name).split())
            if norm not in groups: groups[norm] = []
            groups[norm].append(b)
        
        for norm, b_list in groups.items():
            if len(b_list) > 1:
                # We have duplicates. Pick the first one as primary.
                # Preferably pick one that already has the normalized name.
                primary = next((x for x in b_list if x.name == norm), b_list[0])
                print(f"Merging {len(b_list)-1} duplicates into '{primary.name}' (ID: {primary.id})")
                
                for b in b_list:
                    if b.id == primary.id: continue
                    
                    print(f"  - Merging '{b.name}' (ID: {b.id})")
                    floors = list(Floor.objects.filter(building=b))
                    for f in floors:
                        target_floor, created = Floor.objects.get_or_create(
                            building=primary, 
                            level_number=f.level_number,
                            defaults={'label': f.label}
                        )
                        # Move units
                        Unit.objects.filter(floor=f).update(floor=target_floor)
                        f.delete()
                    
                    b.delete()
            else:
                # Just one building, but maybe name needs normalization
                b = b_list[0]
                if b.name != norm:
                    print(f"Normalizing name: '{b.name}' -> '{norm}'")
                    b.name = norm
                    b.save()

    print("--- Cleanup Complete ---")

if __name__ == '__main__':
    cleanup_duplicate_buildings()
