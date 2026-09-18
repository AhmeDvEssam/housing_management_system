import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Club, Unit, PricingRule
from datetime import date

today = date.today()
month_str = str(today.month)

clubs = Club.objects.all()

print('--- PRICING TEST REPORT ---')
for club in clubs:
    unit = Unit.objects.filter(floor__building__club=club, is_bookable=True).first()
    if not unit:
        print(f'Club: {club.name} - NO BOOKABLE UNITS FOUND')
        continue
        
    print(f'\nClub: {club.name} (Testing Unit {unit.unit_no})')
    
    candidate_rules = PricingRule.objects.filter(clubs=club).prefetch_related('buildings', 'units')
    if not candidate_rules.exists():
        print('  ERROR: No pricing rules assigned to this club!')
        continue
        
    best_score = -1
    best_rule = None
    
    for r in candidate_rules:
        if r.months:
            allowed = [m.strip() for m in r.months.split(',') if m.strip()]
            if allowed and month_str not in allowed: continue
        if r.classifications:
            allowed = [c.strip() for c in r.classifications.split(',') if c.strip()]
            if allowed and unit.classification not in allowed: continue
        if r.unit_types:
            allowed = [t.strip() for t in r.unit_types.split(',') if t.strip()]
            if allowed and unit.unit_type not in allowed: continue
            
        score = 0
        if r.units.filter(id=unit.id).exists(): score += 1000
        if r.buildings.filter(id=unit.floor.building_id).exists(): score += 100
        if r.classifications: score += 50
        if r.unit_types: score += 50
        if r.months: score += 20
        
        if score > best_score:
            best_score = score
            best_rule = r
            
    if best_rule:
        print(f'  Best Rule ID: {best_rule.id} (Score: {best_score})')
        print(f'  - CIVILIAN_GENERAL: {best_rule.price_civilian}')
        print(f'  - MILITARY: {best_rule.price_military}')
        print(f'  - CIVILIAN_AF: {best_rule.price_civilian_af}')
        print(f'  - FAMILY: {best_rule.price_family}')
        
        missing = []
        if not best_rule.price_civilian: missing.append('CIVILIAN_GENERAL')
        if not best_rule.price_military: missing.append('MILITARY')
        if not best_rule.price_civilian_af: missing.append('CIVILIAN_AF')
        if not best_rule.price_family: missing.append('FAMILY')
        
        if missing:
            print('  >>> WARNING: Missing prices for: ' + ', '.join(missing))
    else:
        print('  >>> ERROR: No valid rule matched this unit for the current month/classification!')
