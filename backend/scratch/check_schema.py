import re
with open(r'C:\temp\schema.sql', encoding='utf-8', errors='ignore') as f:
    data = f.read()

m = re.search(r'REM  CREATE TABLE "MIGRATION_TEMP"\."MEMBER_CONTRACT"(.*?);', data, flags=re.DOTALL)
if m:
    print("Found MEMBER_CONTRACT!")
    print(m.group(1)[:1000])
else:
    print("MEMBER_CONTRACT not found in schema.sql")
