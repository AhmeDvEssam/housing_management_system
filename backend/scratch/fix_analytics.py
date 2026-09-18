import sys

# Update analytics_views.py
views_path = r'D:\housing\backend\dashboard\analytics_views.py'
with open(views_path, 'r', encoding='utf-8') as f:
    data = f.read()

# Add global_pt to tree
if "'global_pt':" not in data:
    data = data.replace("tree = {", "tree = {\n            'global_pt': {'civ': {'c':0,'r':0}, 'mil': {'c':0,'r':0}, 'fam': {'c':0,'r':0}, 'mar': {'c':0,'r':0}, 'vet': {'c':0,'r':0}},")

# Accumulate to global_pt inside the loop
# We can find `r = item['rev'] or 0` and inject after it.
inject_code = """
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
"""
if "tree['global_pt']['civ']['c'] += c" not in data:
    data = data.replace("            r = item['rev'] or 0\n", "            r = item['rev'] or 0\n" + inject_code)

with open(views_path, 'w', encoding='utf-8') as f:
    f.write(data)

# Update analytics_dashboard.html
html_path = r'D:\housing\backend\templates\admin\analytics_dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the personTypeChart series to use global_pt
old_series = "series: [{ name: currentViewMode === 'count' ? 'الحجوزات' : 'الإيراد', data: [tree.standard.civ[key], tree.standard.mil[key] + tree.armies.t[key], tree.standard.fam[key], tree.standard.mar[key], tree.standard.vet[key]] }],"
new_series = "series: [{ name: currentViewMode === 'count' ? 'الحجوزات' : 'الإيراد', data: [tree.global_pt.civ[key], tree.global_pt.mil[key], tree.global_pt.fam[key], tree.global_pt.mar[key], tree.global_pt.vet[key]] }],"
html = html.replace(old_series, new_series)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
