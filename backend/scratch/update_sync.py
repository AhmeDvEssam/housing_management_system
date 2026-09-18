import re

def add_safe_str(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    if 'def safe_str(' not in data:
        func = """
def safe_str(val, max_len=255):
    if val is None:
        return ""
    s = str(val).strip()
    return s[:max_len]
"""
        data = data.replace('import io\n', 'import io\n' + func)
        # Apply safe_str to person_name, notes
        data = data.replace("row[1].strip() if row[1] else ''", "safe_str(row[1], 250)")
        data = data.replace("row[38].strip() if row[38] else ''", "safe_str(row[38], 250)")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data)

add_safe_str(r'D:\housing\backend\scripts\smart_sync.py')
try:
    add_safe_str(r'D:\housing\backend\scripts\smart_sync_server.py')
except FileNotFoundError:
    pass
