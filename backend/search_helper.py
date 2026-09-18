import sys
with open(r'D:\housing\backend\templates\dashboard\wallboard.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        ll = line.lower()
        if 'updatekpi' in ll or 'allocated' in ll or 'kpi' in ll:
            sys.stdout.buffer.write(f'{i}: {line.rstrip()}\n'.encode('utf-8'))
