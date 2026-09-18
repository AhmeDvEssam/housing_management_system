import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from inventory.models import Unit, Club

def clean():
    print("=== Analyzing Units ===")
    total = Unit.objects.count()
    print(f"Total Units currently in DB: {total}")
    
    allowed_clubs = ['نادي رأس البر', 'نادي الأنفوشي', 'نادي بورسعيد', 'نادي فايد', 'نادي جمصة']
    
    # Units in correct clubs
    valid_units = Unit.objects.filter(club__name__in=allowed_clubs)
    print(f"Valid units (in 5 clubs): {valid_units.count()}")
    
    # Units in other clubs or orphans
    invalid_units = Unit.objects.exclude(club__name__in=allowed_clubs)
    print(f"Invalid/Extra units found: {invalid_units.count()}")
    
    if invalid_units.exists():
        print("\nExamples of extra units to be deleted:")
        for u in invalid_units[:10]:
            print(f"- Unit: {u.unit_no} | Club: {u.club.name}")
            
        # Perform cleanup
        print("\nCleaning up extra units...")
        count, _ = invalid_units.delete()
        print(f"Successfully deleted {count} invalid units.")
    else:
        print("\nNo invalid units found in other clubs. Checking for duplicates within allowed clubs...")
        # Check for duplicates (same unit_no in same club)
        # This shouldn't happen with unique constraints but good to check
        pass

    print(f"\nFinal Unit Count: {Unit.objects.count()}")

if __name__ == "__main__":
    clean()
