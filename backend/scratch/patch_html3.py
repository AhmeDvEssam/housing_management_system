import os
import re

html_path = r'D:\housing\backend\templates\admin\analytics_dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix sorting of clubData
chart_pattern = r"// 1\. Club Chart.*?let clubSeriesData = currentViewMode === 'count' \? clubData\.map\(d => d\.count \|\| 0\) : clubData\.map\(d => d\.rev \|\| 0\);"

new_code = """
        // 1. Club Chart
        // Sort clubData based on currentViewMode
        clubData.sort((a, b) => {
            if (currentViewMode === 'count') {
                return (b.count || 0) - (a.count || 0);
            } else {
                return (b.rev || 0) - (a.rev || 0);
            }
        });
        
        let clubSeriesData = currentViewMode === 'count' ? clubData.map(d => d.count || 0) : clubData.map(d => d.rev || 0);
"""

html = re.sub(chart_pattern, new_code.strip(), html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
