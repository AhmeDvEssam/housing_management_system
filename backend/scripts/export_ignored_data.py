import os
import sys
import django
import oracledb
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Unit

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

DEFAULT_CLUB_MAP = {
    "21": "نادي راس البر", "22": "نادي راس البر", "23": "نادي راس البر",
    "24": "نادي راس البر", "25": "نادي راس البر", "26": "نادي راس البر",
    "27": "نادي راس البر", "28": "نادي راس البر", "29": "نادي راس البر", "30": "نادي راس البر",
    "4": "فندق الانفوشي",
    "5": "نادي بورسعيد", "6": "نادي بورسعيد", "7": "نادي بورسعيد",
    "11": "نادي بورسعيد", "12": "نادي بورسعيد", "19": "نادي بورسعيد", "20": "نادي بورسعيد",
    "8": "نادي فايد", "9": "نادي فايد", "10": "نادي فايد",
    "31": "نادي جمصة", "32": "نادي جمصة"
}

def export_ignored():
    print("Connecting to Oracle...")
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cursor = conn.cursor()
    
    ignored_contracts = []
    ignored_bookings = []
    
    # Check MEMBER_CONTRACT
    cursor.execute("""
        SELECT mc.MEMBER_CONTRACT_NUM3 as MEMBER_CONTRACT_NUM, mc.MEM_NO, f.PLA_CODE, f.FLAT_NUM, mc.FROM_DATE, mc.TO_DATE
        FROM MEMBER_CONTRACT mc
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
    """)
    contracts = cursor.fetchall()
    
    for row in contracts:
        cont_num, mem_no, pla_code, flat_num, start_d, end_d = row
        pla_str = str(pla_code).strip()
        club_name = DEFAULT_CLUB_MAP.get(pla_str)
        
        unit = None
        if club_name:
            unit = Unit.objects.filter(floor__building__club__name=club_name, unit_no=str(flat_num).strip()).first()
            
        if not unit:
            ignored_contracts.append({
                'Contract Num': cont_num,
                'Member No': mem_no,
                'Oracle PLA_CODE': pla_code,
                'Django Club Mapping': club_name or 'Unmapped',
                'Oracle Flat Num': flat_num,
                'Start Date': start_d,
                'End Date': end_d,
                'Reason': 'Unit does not exist in Data.xlsx'
            })

    # Check PERSON_BOOKED
    cursor.execute("""
        SELECT pb.BOOKING_NUM, pb.MEM_NO, pb.PERSON_NAME, f.PLA_CODE, f.FLAT_NUM, pb.BOOKED_START, pb.BOOKED_END
        FROM PERSON_BOOKED pb
        JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID
    """)
    bookings = cursor.fetchall()
    
    for row in bookings:
        book_num, mem_no, person_name, pla_code, flat_num, start_d, end_d = row
        pla_str = str(pla_code).strip()
        club_name = DEFAULT_CLUB_MAP.get(pla_str)
        
        unit = None
        if club_name:
            unit = Unit.objects.filter(floor__building__club__name=club_name, unit_no=str(flat_num).strip()).first()
            
        if not unit:
            ignored_bookings.append({
                'Booking Num': book_num,
                'Member No': mem_no,
                'Person Name': person_name,
                'Oracle PLA_CODE': pla_code,
                'Django Club Mapping': club_name or 'Unmapped',
                'Oracle Flat Num': flat_num,
                'Start Date': start_d,
                'End Date': end_d,
                'Reason': 'Unit does not exist in Data.xlsx'
            })

    cursor.close()
    conn.close()
    
    output_file = r'd:\housing\ignored_data.xlsx'
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df_contracts = pd.DataFrame(ignored_contracts)
        df_bookings = pd.DataFrame(ignored_bookings)
        
        df_contracts.to_excel(writer, sheet_name='Ignored Contracts', index=False)
        df_bookings.to_excel(writer, sheet_name='Ignored Bookings', index=False)
        
    print(f"Exported ignored data to {output_file}")
    print(f"Total ignored contracts: {len(ignored_contracts)}")
    print(f"Total ignored bookings: {len(ignored_bookings)}")

if __name__ == '__main__':
    export_ignored()
