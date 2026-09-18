import os
import re

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

replacements = {
    r'<link[^>]*href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"[^>]*>': r'<link rel="stylesheet" href="{% static \'css/all.min.css\' %}">',
    r'<script[^>]*src="https://cdn.jsdelivr.net/npm/apexcharts"[^>]*></script>': r'<script src="{% static \'js/apexcharts.min.js\' %}"></script>',
    r'<link[^>]*href="https://fonts.googleapis.com/css2\?family=Cairo[^"]*"[^>]*>': r'<link rel="stylesheet" href="{% static \'css/cairo.css\' %}">',
    r'<link[^>]*href="https://fonts.googleapis.com/css\?family=Source\+Sans\+Pro[^"]*"[^>]*>': r'<link rel="stylesheet" href="{% static \'css/source_sans_pro.css\' %}">',
    r"@import url\('https://fonts.googleapis.com/css2\?family=Cairo[^']+'\);": r"@import url('{% static \'css/cairo.css\' %}');"
}

for root, dirs, files in os.walk(TEMPLATES_DIR):
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            modified = False
            for pattern, replacement in replacements.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True
            
            if modified:
                if '{% load static %}' not in content and '{% extends' not in content:
                    content = '{% load static %}\n' + content
                elif '{% extends' in content and '{% load static %}' not in content:
                    content = re.sub(r'({% extends [^}]+ %})', r'\1\n{% load static %}', content, count=1)

                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(content)
                print(f"Patched: {filepath}")
