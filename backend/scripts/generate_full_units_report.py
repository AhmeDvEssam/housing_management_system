import os
import django
import sys
import oracledb
import pandas as pd
import io

# Setup Django (not needed for Oracle only, but good for context)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')

# Fix encoding for Arabic characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def get_oracle_conn():
    return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)

def main():
    conn = get_oracle_conn()
    cursor = conn.cursor()
    
    # 1. Identify all 31 clubs and their names
    # We'll use a combination of sources. The best source for names seems to be a lookup.
    # If not found, we'll try to find them in transactional tables.
    
    print("--- 1. Listing all Clubs from Oracle ---")
    # We'll try to find a table that has all 31 clubs.
    # Since we found 31 distinct PLA_CODEs in FLAT, we'll try to find their names.
    
    # Let's try to find names by joining FLAT with any table that has PLA_CODE and a name.
    # We'll check CLUB table first (9 rows).
    cursor.execute("SELECT CLUB_CODE, CLUB_NAME FROM CLUB")
    club_names_map = {row[0]: row[1] for row in cursor.fetchall()}
    
    # For others, we'll look into tables that might have them.
    # We'll check every PLA_CODE in FLAT and try to find a name for it.
    cursor.execute("SELECT DISTINCT PLA_CODE FROM FLAT")
    all_pla_codes = [row[0] for row in cursor.fetchall()]
    
    # We'll try to find names in other tables for the missing codes
    missing_codes = [c for c in all_pla_codes if c not in club_names_map]
    
    # Search in tables like PERSON_BOOKED or FLAT descriptions if any
    # Actually, let's just generate the report of all units first.
    
    print(f"Total Clubs identified in FLAT: {len(all_pla_codes)}")
    
    # 2. Generate the units report
    # Name of club, Building No, Unit Type, Unit No
    print("--- 2. Generating Units Report ---")
    
    # Query: Join FLAT with BUILDING
    # FLAT columns: FLAT_NUM, FLAT_ID, PLA_CODE, SLLEEP_ROOM, BED_NUM
    # BUILDING columns: BUILD_NUM, BUILD_NAME, PLA_CODE, BUILD_CODE
    
    query = """
        SELECT 
            f.PLA_CODE, 
            b.BUILD_NUM, 
            f.FLAT_NUM, 
            f.SLLEEP_ROOM, 
            f.BED_NUM
        FROM FLAT f
        LEFT JOIN BUILDING b ON f.PLA_CODE = b.PLA_CODE AND f.FLAT_ROW = b.BUILD_CODE
        ORDER BY f.PLA_CODE, b.BUILD_NUM, f.FLAT_NUM
    """
    
    cursor.execute(query)
    units_data = []
    for row in cursor:
        pla_code, build_num, flat_num, rooms, beds = row
        club_name = club_names_map.get(pla_code, f"نادى كود {pla_code}")
        
        unit_type = f"{rooms} غرف" if rooms else "غير محدد"
        
        units_data.append({
            'كود النادي': pla_code,
            'اسم النادي': club_name,
            'رقم العمارة': build_num or "غير محدد",
            'نوع الوحدة': unit_type,
            'رقم الوحدة': flat_num,
            'عدد السرير': beds
        })
        
    df = pd.DataFrame(units_data)
    
    # Save to Excel
    output_file = 'all_oracle_units_report.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Report saved to {output_file} with {len(units_data)} units.")
    
    # 3. Print the club list to terminal for the user
    print("\n--- Summary of identified Clubs ---")
    unique_clubs = df[['كود النادي', 'اسم النادي']].drop_duplicates().sort_values('كود النادي')
    for _, row in unique_clubs.iterrows():
        print(f"كود: {row['كود النادي']} | الاسم: {row['اسم النادي']}")
        
    conn.close()

if __name__ == "__main__":
    main()
