import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r'D:\housing\import_full_final.log'
data = open(log_path, 'rb').read()
text = data.decode('utf-16-le', errors='replace')
lines = text.split('\n')

target_line = 19807594
print("Context around ORA-00001 for 101580:")
for i in range(target_line - 5, target_line + 45):
    line = lines[i].strip().replace('\x00', '')
    if "IMP-00019:" in line and i > target_line + 5:
        break
    print(f"[{i}] {line}")
