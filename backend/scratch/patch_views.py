import os
import re

py_path = r'D:\housing\backend\dashboard\analytics_views.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

# 1. Update the .values() call in tree_data query
values_old = r"tree_data = list\(qs\.values\('booking_type', 'status', 'person_type', 'army_region', 'pay_method', 'guest_id_no', 'guest_name'\)"
values_new = "tree_data = list(qs.values('booking_type', 'status', 'person_type', 'army_region', 'pay_method', 'guest_id_no', 'guest_name', 'unit__allocation')"
py = re.sub(values_old, values_new, py)

# 2. Update the ALLOCATIONS logic
alloc_old = r"            elif bt == BookingType\.ALLOCATIONS:\s*# If an allocation has a specific person attached.*?tree\['allocations'\]\['t'\]\['r'\] \+= r"
alloc_new = """            elif bt == BookingType.ALLOCATIONS:
                alloc_type = item.get('unit__allocation') or ''
                # If an allocation has a specific person attached (guest_id_no is not empty, or name is a person),
                # it's considered "added to occupied" and the user wants to exclude it from Allocations tally.
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
                        tree['allocations']['permanent']['r'] += r"""

py = re.sub(alloc_old, alloc_new, py, flags=re.DOTALL)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
