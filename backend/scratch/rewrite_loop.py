import sys
import re

views_path = r'D:\housing\backend\dashboard\analytics_views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    data = f.read()

# I will replace the entire loop block
loop_start = data.find('        for item in tree_data:')
loop_end = data.find('        # Chart Data')

if loop_start != -1 and loop_end != -1:
    new_loop = """        for item in tree_data:
            bt = item['booking_type']
            pt = item['person_type']
            st = item['status']
            ar = item['army_region']
            pm = int(item.get('pay_method') or 0)
            gid = item.get('guest_id_no') or ''
            
            raw_c = item['count']
            raw_r = float(item['rev'] or 0)
            
            # Is it confirmed/completed?
            is_confirmed = st in ['مؤكد', 'مكتمل']
            
            # Only accumulate counts & revenues for the main charts if confirmed
            c = raw_c if is_confirmed else 0
            r = raw_r if is_confirmed else 0.0

            # 1. Global Person Types (Main Charts) - confirmed only
            if pt in ['CIVILIAN_GENERAL', 'CIVILIAN_AF']: 
                tree['global_pt']['civ']['c'] += c
                tree['global_pt']['civ']['r'] += r
            elif pt in ['MILITARY', 'ACTIVE_MEMBER']: 
                tree['global_pt']['mil']['c'] += c
                tree['global_pt']['mil']['r'] += r
            elif pt == 'FAMILY_MEMBER': 
                tree['global_pt']['fam']['c'] += c
                tree['global_pt']['fam']['r'] += r
            elif pt == 'MARTYR': 
                tree['global_pt']['mar']['c'] += c
                tree['global_pt']['mar']['r'] += r
            elif pt == 'VETERAN': 
                tree['global_pt']['vet']['c'] += c
                tree['global_pt']['vet']['r'] += r

            # 2. Payments - we use raw_c and raw_r because "Unpaid" implies unconfirmed, and they need to see how many unpaid there are!
            if pm == 1:
                tree['payments']['visa']['c'] += raw_c
                tree['payments']['visa']['r'] += raw_r
            elif pm == 2:
                tree['payments']['bank']['c'] += raw_c
                tree['payments']['bank']['r'] += raw_r
            else:
                tree['payments']['unpaid']['c'] += raw_c
                tree['payments']['unpaid']['r'] += raw_r

            # 3. Booking Types
            if bt == BookingType.STANDARD:
                tree['standard']['t']['c'] += c
                tree['standard']['t']['r'] += r
                
                if pt in ['CIVILIAN_GENERAL', 'CIVILIAN_AF']: 
                    tree['standard']['civ']['c'] += c
                    tree['standard']['civ']['r'] += r
                elif pt in ['MILITARY', 'ACTIVE_MEMBER']: 
                    tree['standard']['mil']['c'] += c
                    tree['standard']['mil']['r'] += r
                elif pt == 'FAMILY_MEMBER': 
                    tree['standard']['fam']['c'] += c
                    tree['standard']['fam']['r'] += r
                elif pt == 'MARTYR': 
                    tree['standard']['mar']['c'] += c
                    tree['standard']['mar']['r'] += r
                elif pt == 'VETERAN': 
                    tree['standard']['vet']['c'] += c
                    tree['standard']['vet']['r'] += r

            elif bt == BookingType.ARMIES_REGIONS:
                tree['armies']['t']['c'] += c
                tree['armies']['t']['r'] += r
                if ar:
                    if ar not in tree['armies']['list']:
                        tree['armies']['list'][ar] = node()
                    tree['armies']['list'][ar]['c'] += c
                    tree['armies']['list'][ar]['r'] += r

            elif bt == BookingType.LOTTERY:
                tree['lottery']['t']['c'] += c
                tree['lottery']['t']['r'] += r
                
                # Lottery sub breakdown needs raw values to show Unconfirmed
                sub = 'confirmed' if is_confirmed else 'unconfirmed'
                tree['lottery'][sub]['t']['c'] += raw_c
                tree['lottery'][sub]['t']['r'] += raw_r
                
                if pt == 'MILITARY': 
                    tree['lottery'][sub]['mil']['c'] += raw_c
                    tree['lottery'][sub]['mil']['r'] += raw_r
                elif pt == 'FAMILY_MEMBER': 
                    tree['lottery'][sub]['fam']['c'] += raw_c
                    tree['lottery'][sub]['fam']['r'] += raw_r
                
            elif bt == BookingType.ALLOCATIONS:
                alloc_type = item.get('unit__allocation') or ''
                is_occupied = bool(gid) and gid != ''
                if not is_occupied:
                    tree['allocations']['t']['c'] += c
                    tree['allocations']['t']['r'] += r
                    
                    if alloc_type == 'ADMINISTRATIVE':
                        tree['allocations']['admin']['c'] += c
                        tree['allocations']['admin']['r'] += r
                    elif alloc_type == 'COMMANDER':
                        tree['allocations']['commander']['c'] += c
                        tree['allocations']['commander']['r'] += r
                    elif alloc_type == 'COMPANY':
                        tree['allocations']['corporate']['c'] += c
                        tree['allocations']['corporate']['r'] += r
                    elif alloc_type == 'PERMANENT':
                        tree['allocations']['permanent']['c'] += c
                        tree['allocations']['permanent']['r'] += r

"""
    data = data[:loop_start] + new_loop + data[loop_end:]
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(data)
    print("Updated views loop.")
