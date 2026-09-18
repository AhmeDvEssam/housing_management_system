import sys
import re
data = open(r'D:\housing\backend\.env', encoding='utf-8').read()
data = re.sub(r'LAST_SYNC_DATE=.*', 'LAST_SYNC_DATE="2000-01-01 00:00:00"', data)
open(r'D:\housing\backend\.env', 'w', encoding='utf-8').write(data)
