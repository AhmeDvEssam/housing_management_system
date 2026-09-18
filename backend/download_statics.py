import os
import urllib.request
import re

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(os.path.join(STATIC_DIR, 'css'), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'js'), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'webfonts'), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, 'fonts'), exist_ok=True)

print("Downloading ApexCharts...")
try:
    urllib.request.urlretrieve("https://cdn.jsdelivr.net/npm/apexcharts", os.path.join(STATIC_DIR, 'js', 'apexcharts.min.js'))
except Exception as e:
    print(e)

print("Downloading FontAwesome...")
fa_css_url = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
fa_css_path = os.path.join(STATIC_DIR, 'css', 'all.min.css')
try:
    urllib.request.urlretrieve(fa_css_url, fa_css_path)
    fonts = ['fa-solid-900.woff2', 'fa-regular-400.woff2', 'fa-brands-400.woff2', 'fa-v4compatibility.woff2']
    for f in fonts:
        urllib.request.urlretrieve(f"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/{f}", os.path.join(STATIC_DIR, 'webfonts', f))
except Exception as e:
    print(e)

print("Downloading Cairo Font...")
cairo_css_url = "https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap"
try:
    req = urllib.request.Request(cairo_css_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/100.0.0.0'})
    css_content = urllib.request.urlopen(req).read().decode('utf-8')
    urls = re.findall(r'url\((https://[^)]+\.woff2)\)', css_content)
    for i, url in enumerate(set(urls)):
        font_name = f"cairo_{i}.woff2"
        urllib.request.urlretrieve(url, os.path.join(STATIC_DIR, 'fonts', font_name))
        css_content = css_content.replace(url, f"../fonts/{font_name}")
    with open(os.path.join(STATIC_DIR, 'css', 'cairo.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)
except Exception as e:
    print(e)

print("Downloading Source Sans Pro...")
ssp_url = "https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700"
try:
    req = urllib.request.Request(ssp_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/100.0.0.0'})
    css_content = urllib.request.urlopen(req).read().decode('utf-8')
    urls = re.findall(r'url\((https://[^)]+\.woff2)\)', css_content)
    for i, url in enumerate(set(urls)):
        font_name = f"ssp_{i}.woff2"
        urllib.request.urlretrieve(url, os.path.join(STATIC_DIR, 'fonts', font_name))
        css_content = css_content.replace(url, f"../fonts/{font_name}")
    with open(os.path.join(STATIC_DIR, 'css', 'source_sans_pro.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)
except Exception as e:
    print(e)

print("Done downloading statics!")
