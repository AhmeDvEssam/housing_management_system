from inventory.models import Club
bad_names = ['فايد', 'راس البر', 'جمصة', 'بورسعيد', 'الانفوشى']
deleted, _ = Club.objects.filter(name__in=bad_names).delete()
print(f"Deleted {deleted} bad clubs.")
