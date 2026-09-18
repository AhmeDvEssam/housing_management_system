import sys
data = open(r'D:\housing\backend\scratch\compare_2025.py', encoding='utf-8').read()
data += """
print("Oracle 34241:", [x for x in oracle_records if x.get("mem_no") == 34241])
print("Oracle 85985:", [x for x in oracle_records if x.get("mem_no") == 85985])
print("Django 34241:", [x for x in django_records if x.get("mem_no") == '34241'])
print("Django 85985:", [x for x in django_records if x.get("mem_no") == '85985'])
print("Missing 34241:", [x for x in missing_in_django if x.get("mem_no") == 34241])
print("Missing 85985:", [x for x in missing_in_django if x.get("mem_no") == 85985])
"""
with open(r'D:\housing\backend\scratch\debug_compare.py', 'w', encoding='utf-8') as f:
    f.write(data)
