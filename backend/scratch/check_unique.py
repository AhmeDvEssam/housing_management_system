import re
with open(r'C:\temp\schema.sql', encoding='utf-8', errors='ignore') as f:
    data = f.read()

m = re.search(r'CONSTRAINT "MEMBER_CONTRACT_U01" UNIQUE \((.*?)\)', data, flags=re.DOTALL)
if m:
    print("Unique constraint columns:", m.group(1).replace('\n', '').replace('REM', ''))
else:
    print("Unique constraint not found in schema.sql")
