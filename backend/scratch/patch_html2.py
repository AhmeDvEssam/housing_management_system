import os
import re

html_path = r'D:\housing\backend\templates\admin\analytics_dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the personTypeChart data to include armies in military
chart_pattern = r"data: \[tree\.standard\.civ\[key\], tree\.standard\.mil\[key\], tree\.standard\.fam\[key\], tree\.standard\.mar\[key\], tree\.standard\.vet\[key\]\]"
replacement = "data: [tree.standard.civ[key], tree.standard.mil[key] + tree.armies.t[key], tree.standard.fam[key], tree.standard.mar[key], tree.standard.vet[key]]"

html = re.sub(chart_pattern, replacement, html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
