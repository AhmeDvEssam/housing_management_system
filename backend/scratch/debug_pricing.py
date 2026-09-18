"""Debug pricing rules - UTF-8 safe."""
import os, sys, django, io, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import PricingRule, Unit, Club

rules_data = []
for r in PricingRule.objects.all():
    rules_data.append({
        "id": r.id,
        "clubs": list(r.clubs.values_list("name", flat=True)),
        "buildings": list(r.buildings.values_list("name", flat=True)),
        "months": r.months,
        "unit_types": r.unit_types,
        "classifications": r.classifications,
        "view_types": r.view_types,
        "price_military": float(r.price_military) if r.price_military is not None else 0,
        "price_family": float(r.price_family) if r.price_family is not None else 0,
        "price_civilian_af": float(r.price_civilian_af) if r.price_civilian_af is not None else 0,
        "price_civilian": float(r.price_civilian) if r.price_civilian is not None else 0,
        "price_martyr": float(r.price_martyr) if r.price_martyr is not None else 0,
        "price_veteran": float(r.price_veteran) if r.price_veteran is not None else 0
    })

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'current_prices.json'), 'w', encoding='utf-8') as f:
    json.dump(rules_data, f, ensure_ascii=False, indent=2)

print("Success")
