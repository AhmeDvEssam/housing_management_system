import sys, os
sys.path.append('d:/housing/backend/scripts')
import smart_sync
conn = smart_sync.get_oracle_conn()
cursor = conn.cursor()
cursor.execute("SELECT column_name FROM user_tab_columns WHERE table_name = 'FLAT'")
print([r[0] for r in cursor.fetchall()])
cursor.close()
conn.close()
