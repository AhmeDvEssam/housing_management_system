import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r'D:\housing\import_full_final.log'
data = open(log_path, 'rb').read()
text = data.decode('utf-16-le', errors='replace')
lines = text.split('\n')

# Look at the MEMBER_CONTRACT section for the ACTUAL Oracle error details  
# The error detail (ORA-XXXXX) usually appears on the line AFTER "IMP-00019"
mc_start = 19308199
mc_end = 19845225

print("=== Looking at first few rejected rows with full context ===\n")

count = 0
for i in range(mc_start, min(mc_start + 500, mc_end)):
    clean = lines[i].strip().replace('\r', '').replace('\x00', '')
    if clean:
        print(f"[{i}] {clean}")
    if count > 200:
        break
    if clean:
        count += 1

print("\n\n=== Looking for ORA- error codes in MEMBER_CONTRACT section ===")
ora_errors = {}
for i in range(mc_start, mc_end):
    clean = lines[i].strip().replace('\r', '').replace('\x00', '')
    if 'ORA-' in clean:
        # Extract ORA code
        import re
        matches = re.findall(r'ORA-\d+', clean)
        for m in matches:
            ora_errors[m] = ora_errors.get(m, 0) + 1

print(f"Distinct ORA errors found: {ora_errors}")
