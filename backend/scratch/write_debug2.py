import sys
data = open(r'D:\housing\backend\scratch\compare_2025.py', encoding='utf-8').read()
data += """
print("12051 in Oracle:", [x for x in oracle_records if x.get("mem_no") == 12051])
print("12051 in Django:", [x for x in django_records if x.get("mem_no") == '12051'])
"""
with open(r'D:\housing\backend\scratch\debug_compare2.py', 'w', encoding='utf-8') as f:
    f.write(data)
