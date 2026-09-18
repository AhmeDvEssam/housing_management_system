import sys
sys.stdout.reconfigure(encoding='utf-8')

# Read the import log and find MEMBER_CONTRACT rejected rows
log_path = r'D:\housing\import_full_final.log'

data = open(log_path, 'rb').read()
text = data.decode('utf-16-le', errors='replace')
lines = text.split('\n')

print(f"Total lines in log: {len(lines)}")

# Find sections related to MEMBER_CONTRACT
in_mc_section = False
mc_errors = []
mc_section_start = -1

for i, line in enumerate(lines):
    clean = line.strip().replace('\r', '').replace('\x00', '')
    
    # Detect table import section
    if 'importing table' in clean.lower() and 'MEMBER_CONTRACT' in clean:
        in_mc_section = True
        mc_section_start = i
        print(f"\n=== MEMBER_CONTRACT section starts at line {i}: {clean}")
    
    if in_mc_section:
        if 'IMP-00019' in clean or 'ORA-12899' in clean or 'row rejected' in clean or 'value too large' in clean:
            mc_errors.append((i, clean))
        
        # End of section
        if 'importing table' in clean.lower() and 'MEMBER_CONTRACT' not in clean and i > mc_section_start + 5:
            in_mc_section = False
            print(f"=== MEMBER_CONTRACT section ends at line {i}")

print(f"\nTotal MEMBER_CONTRACT rejection errors: {len(mc_errors)}")
for idx, (line_no, err) in enumerate(mc_errors[:50]):
    print(f"  [{line_no}] {err}")

# Also search broadly for any 12899 errors mentioning MEMBER_CONTRACT
print("\n\n=== Searching ALL ORA-12899 errors in entire log ===")
all_12899 = []
for i, line in enumerate(lines):
    clean = line.strip().replace('\r', '').replace('\x00', '')
    if 'ORA-12899' in clean:
        # Get surrounding context (5 lines before and after)
        context_start = max(0, i-3)
        context_end = min(len(lines), i+3)
        context = []
        for j in range(context_start, context_end):
            ctx = lines[j].strip().replace('\r', '').replace('\x00', '')
            if ctx:
                context.append(f"  [{j}] {ctx}")
        all_12899.append((i, clean, context))

print(f"Total ORA-12899 in log: {len(all_12899)}")
for idx, (line_no, err, ctx) in enumerate(all_12899):
    print(f"\n--- Error #{idx+1} at line {line_no} ---")
    for c in ctx:
        print(c)
