import sys
sys.stdout.reconfigure(encoding='utf-8')

log_path = r'D:\housing\import_full_final.log'
data = open(log_path, 'rb').read()
text = data.decode('utf-16-le', errors='replace')
lines = text.split('\n')

mc_start = 19308199
mc_end = 19845225

found_rows = []
current_row = {}
for i in range(mc_start, mc_end):
    line = lines[i].strip().replace('\x00', '')
    if line.startswith("IMP-00019:"):
        current_row = {}
    elif line.startswith("Column 1 "):
        current_row[1] = line.replace("Column 1 ", "")
    elif line.startswith("Column 2 "):
        current_row[2] = line.replace("Column 2 ", "")
    elif line.startswith("Column 3 "):
        current_row[3] = line.replace("Column 3 ", "")
    elif line.startswith("Column 4 "):
        current_row[4] = line.replace("Column 4 ", "")
    elif line.startswith("Column 5 "):
        current_row[5] = line.replace("Column 5 ", "")
    elif line.startswith("Column 6 "):
        current_row[6] = line.replace("Column 6 ", "")
        
        if current_row.get(5) == '666' and current_row.get(2) == '23-MAY-2026:00:00:00' and current_row.get(3) == '9':
            print("Found rejected row matching flat 666 and date:", current_row)

