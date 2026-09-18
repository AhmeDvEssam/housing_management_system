import re
with open(r'C:\temp\schema.sql', encoding='utf-8', errors='ignore') as f:
    data = f.read()

m = re.search(r'REM  CREATE TABLE "MIGRATION_TEMP"\."MEMBER_CONTRACT"(.*?);', data, flags=re.DOTALL)
if m:
    part = m.group(1)
    notes_match = re.search(r'\"NOTES\"[^,]+', part)
    if notes_match:
        print("NOTES format:", notes_match.group(0))
    else:
        print("NOTES not found")
