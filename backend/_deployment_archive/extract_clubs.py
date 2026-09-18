import oracledb
import json

conn = oracledb.connect(user='MIGRATION_TEMP', password='migration', dsn='localhost:1521/xe')
c = conn.cursor()

c.execute('SELECT CLUB_CODE, CLUB_NAME FROM CLUB')
clubs = {row[0]: row[1] for row in c.fetchall()}

c.execute('SELECT PLA_CODE, PLA_NAME, CLUB_CODE FROM BUILDING')
buildings = [{'pla_code': row[0], 'pla_name': row[1], 'club_code': row[2]} for row in c.fetchall()]

output = {
    'clubs': clubs,
    'buildings': buildings
}

with open('db_structure.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

conn.close()
