import glob, os

bat_dir = r'D:\housing\Bat_Files'
for bat_file in glob.glob(os.path.join(bat_dir, '*.bat')):
    try:
        with open(bat_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(bat_file, 'r', encoding='cp1256') as f:
            content = f.read()
    
    if 'cd /d "%~dp0"' in content and 'cd /d "%~dp0\.."' not in content:
        new_content = content.replace('cd /d "%~dp0"', 'cd /d "%~dp0\.."')
        try:
            with open(bat_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
        except Exception:
            with open(bat_file, 'w', encoding='cp1256') as f:
                f.write(new_content)
        print(f'Fixed {os.path.basename(bat_file)}')
