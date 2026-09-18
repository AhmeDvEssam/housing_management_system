import os
import re

py_path = r'D:\housing\backend\dashboard\analytics_views.py'
with open(py_path, 'r', encoding='utf-8') as f:
    py = f.read()

# Fix ACTIVE_MEMBER not being counted as military in the dashboard
old = r"elif pt == 'MILITARY':"
new = r"elif pt in ['MILITARY', 'ACTIVE_MEMBER']:"
py = re.sub(old, new, py)

with open(py_path, 'w', encoding='utf-8') as f:
    f.write(py)
