import oracledb
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def main():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    # Attempt to build a code -> name map using CONTWIN1 join
    print("--- Building Club Map from FLAT + CONTWIN1 ---")
    query_map = """
        SELECT DISTINCT f.PLA_CODE, c.CLUB_NAME
        FROM FLAT f
        JOIN CONTWIN1 c ON f.FLAT_ID = c.FLAT_ID
    """
    club_map = {}
    try:
        cursor.execute(query_map)
        for row in cursor:
            club_map[row[0]] = row[1]
    except Exception as e:
        print(f"Error building map: {e}")

    # Add names from CLUB table too
    try:
        cursor.execute("SELECT CLUB_CODE, CLUB_NAME FROM CLUB")
        for row in cursor:
            if row[0] not in club_map:
                club_map[row[0]] = row[1]
    except: pass
    
    print(f"Mapped {len(club_map)} clubs.")
    
    # 31 clubs check
    cursor.execute("SELECT DISTINCT PLA_CODE FROM FLAT")
    all_codes = [r[0] for r in cursor.fetchall()]
    
    print("\n--- FINAL REPORT GENERATION ---")
    units_data = []
    # Fetch all units
    cursor.execute("SELECT PLA_CODE, FLAT_ROW, SLLEEP_ROOM, FLAT_NUM FROM FLAT ORDER BY PLA_CODE, FLAT_ROW, FLAT_NUM")
    for row in cursor:
        pla_code, flat_row, rooms, flat_num = row
        name = club_map.get(pla_code, f"نادى غير معروف (كود {pla_code})")
        units_data.append({
            'اسم النادي': name,
            'رقم العمارة': flat_row,
            'نوع الوحدة': f"{rooms} غرف" if rooms else "غرفة",
            'رقم الوحدة': flat_num,
            'كود النادي': pla_code
        })
        
    import pandas as pd
    df = pd.DataFrame(units_data)
    df.to_excel('all_oracle_units_final.xlsx', index=False)
    print(f"Exported {len(units_data)} units to all_oracle_units_final.xlsx")
    
    # Summary of clubs for user
    print("\n--- List of Identified Clubs (31 total target) ---")
    summary = df[['كود النادي', 'اسم النادي']].drop_duplicates().sort_values('كود النادي')
    for _, r in summary.iterrows():
        print(f"Code {r['كود النادي']} : {r['اسم النادي']}")
        
    conn.close()

if __name__ == "__main__":
    main()
