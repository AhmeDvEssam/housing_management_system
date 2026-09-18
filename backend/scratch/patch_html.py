import os
import re

html_path = r'D:\housing\backend\templates\admin\analytics_dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update armiesHtml loop
html = html.replace('tree.standard.armies', 'tree.armies.list')

# 2. Update tree labels for Standard vs Armies
html = html.replace('<span><i class="fas fa-chevron-left"></i> الحجوزات العادية والجيوش</span>', '<span><i class="fas fa-chevron-left"></i> الحجوزات العادية (أيام)</span>')

# The army node is currently nested inside Standard. Let's extract it.
old_standard = """
                <!-- Standard Bookings -->
                <div class="tree-node">
                    <div class="tree-label" onclick="toggleNode(this)">
                        <span><i class="fas fa-chevron-left"></i> الحجوزات العادية (أيام)</span>
                        <span class="badge">${val(tree.standard.t)}</span>
                    </div>
                    <div class="tree-children">
                        <div class="leaf-node"><span>مدني عام</span><span>${val(tree.standard.civ)}</span></div>
                        <div class="tree-node">
                            <div class="tree-label" onclick="toggleNode(this)" style="background: rgba(2, 132, 199, 0.1);">
                                <span><i class="fas fa-chevron-down"></i> عسكري (الجيوش والمناطق)</span>
                                <span class="badge">${val(tree.standard.mil)}</span>
                            </div>
                            <div class="tree-children active">
                                ${armiesHtml}
                            </div>
                        </div>
                        <div class="leaf-node"><span>عضوية عائلية</span><span>${val(tree.standard.fam)}</span></div>
                        <div class="leaf-node"><span>شهيد</span><span>${val(tree.standard.mar)}</span></div>
                        <div class="leaf-node"><span>محارب</span><span>${val(tree.standard.vet)}</span></div>
                    </div>
                </div>
"""

new_standard_and_armies = """
                <!-- Standard Bookings -->
                <div class="tree-node">
                    <div class="tree-label" onclick="toggleNode(this)" style="background: rgba(2, 132, 199, 0.1);">
                        <span><i class="fas fa-chevron-left"></i> الحجوزات العادية (أيام)</span>
                        <span class="badge" style="background: #0284c7;">${val(tree.standard.t)}</span>
                    </div>
                    <div class="tree-children">
                        <div class="leaf-node"><span>مدني عام</span><span>${val(tree.standard.civ)}</span></div>
                        <div class="leaf-node"><span>عسكري</span><span>${val(tree.standard.mil)}</span></div>
                        <div class="leaf-node"><span>عضوية عائلية</span><span>${val(tree.standard.fam)}</span></div>
                        <div class="leaf-node"><span>شهيد</span><span>${val(tree.standard.mar)}</span></div>
                        <div class="leaf-node"><span>محارب</span><span>${val(tree.standard.vet)}</span></div>
                    </div>
                </div>

                <!-- Armies Bookings -->
                <div class="tree-node">
                    <div class="tree-label" onclick="toggleNode(this)" style="background: rgba(16, 185, 129, 0.1);">
                        <span><i class="fas fa-chevron-left"></i> حجوزات الجيوش والمناطق</span>
                        <span class="badge" style="background: #10b981;">${val(tree.armies.t)}</span>
                    </div>
                    <div class="tree-children">
                        ${armiesHtml}
                    </div>
                </div>
"""

# Find the old standard block dynamically if possible
import re
pattern = re.compile(r'<!-- Standard Bookings -->.*?<!-- Lottery Bookings -->', re.DOTALL)
html = pattern.sub(new_standard_and_armies.strip() + '\n\n                <!-- Lottery Bookings -->', html)


# 3. Update initChart for bookingTypeChart
chart_pattern = r"initChart\('bookingTypeChart'.*?series: \[tree\.standard\.t\[key\], tree\.lottery\.t\[key\], tree\.allocations\.t\[key\]\].*?labels: \['حجز عادي وجيوش', 'قرعة', 'مخصصات'\].*?colors: \['#0284c7', '#d97706', '#4f46e5'\].*?\}\);"
new_chart = """
        initChart('bookingTypeChart', {
            chart: { type: 'donut', height: 300, animations: { dynamicAnimation: { speed: 1000 } } },
            series: [tree.standard.t[key], tree.armies.t[key], tree.lottery.t[key], tree.allocations.t[key]],
            labels: ['حجز عادي (أيام)', 'جيوش ومناطق', 'قرعة', 'مخصصات'],
            colors: ['#0284c7', '#10b981', '#d97706', '#4f46e5'],
            dataLabels: { enabled: false }
        });
"""

html = re.sub(chart_pattern, new_chart.strip(), html, flags=re.DOTALL)


# 4. Update army chart logic
html = html.replace('const armies = tree.standard.armies;', 'const armies = tree.armies.list;')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML Patched!")
