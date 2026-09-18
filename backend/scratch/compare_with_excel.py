import oracledb
import os
import sys
import io
import openpyxl

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

CLUB_MAP = {
    21: 'نادي راس البر', 22: 'نادي راس البر', 23: 'نادي راس البر',
    24: 'نادي راس البر', 25: 'نادي راس البر', 26: 'نادي راس البر',
    27: 'نادي راس البر', 28: 'نادي راس البر', 29: 'نادي راس البر',
    30: 'نادي راس البر',
    4: 'فندق الانفوشي',
    5: 'نادي بورسعيد', 6: 'نادي بورسعيد', 7: 'نادي بورسعيد',
    11: 'نادي بورسعيد', 12: 'نادي بورسعيد',
    19: 'نادي بورسعيد', 20: 'نادي بورسعيد',
    8: 'نادي فايد', 9: 'نادي فايد', 10: 'نادي فايد',
    31: 'نادي جمصة', 32: 'نادي جمصة',
}

LOTTERY_CLUB_MAP = {
    'نادى 6 اكتوبر الانفوشى': 'فندق الانفوشي',
    'نادى 6 اكتوبر بورسعيد': 'نادي بورسعيد',
    'نادى 6 اكتوبر رأس البر': 'نادي راس البر',
    'نادى 6 اكتوبر فايـــد': 'نادي فايد',
    'نادى 6 اكتوبر جمصــــه': 'نادي جمصة',
}

def main():
    excel_path = r"D:\housing\تحليل\نتيجه قرعة 2026.xlsx"
    if not os.path.exists(excel_path):
        print(f"Excel file not found at {excel_path}")
        return

    print("--- Reading Excel sheet ---")
    wb = openpyxl.load_workbook(excel_path, read_only=True)
    ws = wb.active
    
    excel_records = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if len(row) < 7: continue
        _, mem_no_val, member_name, club_name, unit_desc, unit_no_val, period_val = row[:7]
        if mem_no_val is None: continue
        membership_no = str(int(mem_no_val))
        unit_no = str(int(unit_no_val)) if unit_no_val is not None else ''
        period_no = int(period_val) if period_val is not None else 0
        excel_records[membership_no] = {
            'club_name': club_name,
            'unit_no': unit_no,
            'period_no': period_no,
            'member_name': member_name
        }
    wb.close()
    print(f"Total records in Excel: {len(excel_records)}")

    print("\n--- Reading WIN_TEMP from Oracle ---")
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
        cursor = conn.cursor()
        query = """
            SELECT wt.MEM_NO, f.PLA_CODE, f.FLAT_NUM, wt.FTRA_ID, wt.WISH_NO, wt.FLAT_PRICE
            FROM WIN_TEMP wt
            LEFT JOIN FLAT f ON wt.FLAT_ID = CAST(f.FLAT_ID AS VARCHAR2(50))
            WHERE wt.START_FIRST_FTRA_DATE = TO_DATE('2026-05-23', 'YYYY-MM-DD')
        """
        cursor.execute(query)
        oracle_rows = cursor.fetchall()
        
        matches = 0
        mismatch = 0
        not_in_excel = 0
        
        for row in oracle_rows:
            mem_no, pla_code, flat_num, ftra_id, wish_no, price = row
            mem_no_str = str(mem_no)
            
            if mem_no_str in excel_records:
                excel_rec = excel_records[mem_no_str]
                # Compare
                django_club_oracle = CLUB_MAP.get(pla_code)
                django_club_excel = LOTTERY_CLUB_MAP.get(excel_rec['club_name'].strip())
                
                oracle_unit = str(flat_num).strip()
                excel_unit = str(excel_rec['unit_no']).strip()
                
                oracle_period = int(ftra_id)
                excel_period = int(excel_rec['period_no'])
                
                club_match = (django_club_oracle == django_club_excel)
                unit_match = (oracle_unit == excel_unit)
                period_match = (oracle_period == excel_period)
                
                if club_match and unit_match and period_match:
                    matches += 1
                else:
                    mismatch += 1
                    if mismatch <= 5:
                        print(f"Mismatch for Member {mem_no_str}:")
                        print(f"  Oracle: Club='{django_club_oracle}', Unit='{oracle_unit}', Period={oracle_period}")
                        print(f"  Excel:  Club='{django_club_excel}', Unit='{excel_unit}', Period={excel_period}")
            else:
                not_in_excel += 1
                
        print(f"\nComparison Results:")
        print(f"  - Matches (Perfect): {matches}")
        print(f"  - Mismatch (Same member but different unit/club/period): {mismatch}")
        print(f"  - In Oracle but not in Excel: {not_in_excel}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
