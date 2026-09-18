import os
try:
    os.remove(r'D:\housing\backend\pg_backup.bat')
    os.remove(r'D:\housing\backend\pg_restore.bat')
except Exception:
    pass
