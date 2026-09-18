import sys, re
sys.stdout.reconfigure(encoding='utf-8')

log_path = r'D:\housing\import_full_final.log'
data = open(log_path, 'rb').read()
text = data.decode('utf-16-le', errors='replace')
lines = text.split('\n')

missing_members = ['75698', '48442', '91165', '83013', '101580', '82907', '79880', '85018', '49607', '37032', '85571', '79450']
mc_start = 19308199
mc_end = 19845225

found_members = {m: [] for m in missing_members}

for i in range(mc_start, mc_end):
    clean = lines[i].strip().replace('\r', '').replace('\x00', '')
    if clean.startswith("Column 6"):
        val = clean.replace("Column 6 ", "").strip()
        if val in missing_members:
            found_members[val].append(i)

print("Checking if missing members were rejected in MEMBER_CONTRACT due to ORA-00001:")
for mem, locs in found_members.items():
    print(f"Mem_No {mem}: rejected {len(locs)} times")
    if locs:
        # Show the first rejection reason
        for j in range(max(mc_start, locs[0]-8), locs[0]+2):
            print(f"  [{j}] {lines[j].strip().replace(chr(0), '')}")

