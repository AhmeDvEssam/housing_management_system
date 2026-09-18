data = open(r'D:\housing\Bat_Files\precreate_tables.sql', encoding='utf-8').read()
import re
print("CREATE TABLE count:")
for line in data.split('\n'):
    if 'CREATE TABLE' in line:
        print(line[:50])
