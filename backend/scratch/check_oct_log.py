import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check imp_oct.log for ORA-12899 and MEMBER_CONTRACT errors
log_path = r'D:\housing\imp_oct.log'
data = open(log_path, 'rb').read()

# Try different encodings
for enc in ['utf-8', 'utf-16-le', 'utf-16', 'cp1256', 'latin-1']:
    try:
        text = data.decode(enc, errors='replace')
        if 'MEMBER_CONTRACT' in text or 'IMP-' in text:
            print(f"Decoded with: {enc}")
            break
    except:
        continue

lines = text.split('\n')
print(f"Total lines: {len(lines)}")

# Search for ORA-12899
ora_12899 = []
for i, line in enumerate(lines):
    clean = line.strip().replace('\r', '').replace('\x00', '')
    if 'ORA-12899' in clean:
        ora_12899.append((i, clean))

print(f"\nORA-12899 errors: {len(ora_12899)}")
for idx, (ln, txt) in enumerate(ora_12899[:30]):
    # Get context
    for j in range(max(0, ln-2), min(len(lines), ln+5)):
        ctx = lines[j].strip().replace('\r', '').replace('\x00', '')
        if ctx:
            print(f"  [{j}] {ctx}")
    print()

# Search for MEMBER_CONTRACT section
mc_sections = []
for i, line in enumerate(lines):
    clean = line.strip().replace('\r', '').replace('\x00', '')
    if 'MEMBER_CONTRACT' in clean and 'importing' in clean.lower():
        mc_sections.append((i, clean))

print(f"\nMEMBER_CONTRACT import sections: {len(mc_sections)}")
for ln, txt in mc_sections:
    print(f"  [{ln}] {txt}")

# All ORA errors in the whole file
all_ora = {}
for line in lines:
    clean = line.strip().replace('\r', '').replace('\x00', '')
    if 'ORA-' in clean:
        import re
        for m in re.findall(r'ORA-\d+', clean):
            all_ora[m] = all_ora.get(m, 0) + 1

print(f"\nAll ORA error types: {all_ora}")
