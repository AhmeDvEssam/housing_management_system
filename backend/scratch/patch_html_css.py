import os
import re

html_path = r'D:\housing\backend\templates\admin\analytics_dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Remove max-height and overflow-y from .tree-card
html = re.sub(r'max-height:\s*1000px;', '', html)
html = re.sub(r'overflow-y:\s*auto;', '', html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
