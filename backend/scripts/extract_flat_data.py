"""
Extract flat/unit data from Oracle to help map flat_id to Data.xlsx units.
This will output: Club Code (PLA_CODE), Club Name, Building (PLA_CODE), Unit Number (FLAT_NUM), Flat ID (FLAT_ID), Classification
"""
import os
import sys
import oracledb
import csv

# Oracle Connection Config
ORACLE_USER = os.environ.get('ORACLE_USER', 'oct')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'oct_123')
ORACLE_DSN = os.environ.get('ORACLE_DSN', '192.168.1.90:1521/orcl')

CLUB_MAP = {
    "21": "نادي راس البر", "22": "نادي راس البر", "23": "نادي راس البر",
    "24": "نادي راس البر", "25": "نادي راس البر", "26": "نادي راس البر",
    "27": "نادي راس البر", "28": "نادي راس البر", "29": "نادي راس البر", "30": "نادي راس البر",
    "4": "فندق الانفوشي",
    "5": "نادي بورسعيد", "6": "نادي بورسعيد", "7": "نادي بورسعيد",
    "11": "نادي بورسعيد", "12": "نادي بورسعيد", "19": "نادي بورسعيد", "20": "نادي بورسعيد",
    "8": "نادي فايد", "9": "نادي فايد", "10": "نادي فايد",
    "31": "نادي جمصة", "32": "نادي جمصة"
}

def get_oracle_conn():
    try:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            client_dir = os.path.join(base_dir, 'instantclient')
            if os.path.exists(client_dir):
                oracledb.init_oracle_client(lib_dir=client_dir)
            else:
                oracledb.init_oracle_client()
        except Exception:
            pass
        return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    except Exception as e:
        print(f"[ERROR] Could not connect to Oracle: {e}")
        return None

if __name__ == "__main__":
    conn = get_oracle_conn()
    if not conn:
        print("[FAILED] Cannot connect to Oracle.")
        sys.exit(1)

    club_ids = tuple(int(k) for k in CLUB_MAP.keys())
    
    cursor = conn.cursor()
    
    query = f"""
        SELECT f.FLAT_ID, f.FLAT_NUM, f.PLA_CODE, f.FLAT_TYPE, f.FLAT_CLASSIFICATION
        FROM FLAT f
        WHERE f.PLA_CODE IN {club_ids}
        ORDER BY f.PLA_CODE, f.FLAT_NUM
    """
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'flat_data_export.csv')
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['FLAT_ID', 'FLAT_NUM', 'PLA_CODE', 'CLUB_NAME', 'FLAT_TYPE', 'FLAT_CLASSIFICATION'])
            
            for row in rows:
                flat_id, flat_num, pla_code, flat_type, flat_class = row
                club_name = CLUB_MAP.get(str(pla_code), f"Unknown ({pla_code})")
                writer.writerow([flat_id, flat_num, pla_code, club_name, flat_type, flat_class])
        
        print(f"\n[SUCCESS] Exported {len(rows)} units to: {output_path}", flush=True)
        
        # Show Gamsa specifically
        print(f"\n--- نادي جمصة (Codes 31, 32) - Duplicates Check ---", flush=True)
        gamsa_query = f"""
            SELECT f.FLAT_ID, f.FLAT_NUM, f.PLA_CODE, f.FLAT_TYPE, f.FLAT_CLASSIFICATION
            FROM FLAT f
            WHERE f.PLA_CODE IN (31, 32)
            ORDER BY f.FLAT_NUM, f.PLA_CODE
        """
        cursor.execute(gamsa_query)
        gamsa_rows = cursor.fetchall()
        
        print(f"{'FLAT_ID':<10} {'FLAT_NUM':<12} {'PLA_CODE':<10} {'BUILDING':<12} {'TYPE':<15} {'CLASSIFICATION'}", flush=True)
        print("-" * 80, flush=True)
        for row in gamsa_rows:
            flat_id, flat_num, pla_code, flat_type, flat_class = row
            building = "عمارة 1" if pla_code == 31 else "عمارة 2"
            print(f"{flat_id:<10} {flat_num:<12} {pla_code:<10} {building:<12} {str(flat_type):<15} {flat_class}", flush=True)
        
        # Show duplicates
        print(f"\n--- Duplicate FLAT_NUMs in Gamsa ---", flush=True)
        seen = {}
        for row in gamsa_rows:
            flat_id, flat_num, pla_code, flat_type, flat_class = row
            key = str(flat_num)
            if key not in seen:
                seen[key] = []
            seen[key].append((flat_id, pla_code))
        
        dup_count = 0
        for flat_num, entries in sorted(seen.items()):
            if len(entries) > 1:
                dup_count += 1
                print(f"  Unit {flat_num}: ", end="", flush=True)
                for flat_id, pla_code in entries:
                    building = "عمارة 1" if pla_code == 31 else "عمارة 2"
                    print(f"[FLAT_ID={flat_id}, {building}] ", end="", flush=True)
                print(flush=True)
        
        if dup_count == 0:
            print("  No duplicates found.", flush=True)
        else:
            print(f"\n  Total duplicated unit numbers: {dup_count}", flush=True)
                
    except Exception as e:
        print(f"[ERROR] Query failed: {e}", flush=True)
    finally:
        cursor.close()
        conn.close()
