import os
import sys
import oracledb
import pandas as pd
import io

# Fix encoding for Arabic
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def generate_report():
    print("=== Generating 2026 Data Analysis Report ===")
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
        cursor = conn.cursor()
        
        # 1. Total Members
        cursor.execute("SELECT COUNT(*) FROM MEMBER")
        total_members = cursor.fetchone()[0]
        
        # 2. Contracts in 2026
        cursor.execute("SELECT COUNT(*) FROM MEMBER_CONTRACT WHERE FOR_YEAR = 2026")
        contracts_2026 = cursor.fetchone()[0]
        
        # 3. Bookings in 2026
        cursor.execute("SELECT COUNT(*) FROM PERSON_BOOKED WHERE TO_CHAR(RECORD_DATE, 'YYYY') = '2026'")
        bookings_2026 = cursor.fetchone()[0]
        
        # 4. Forms (Estmara)
        cursor.execute("SELECT COUNT(*) FROM MEMBER_ESTMARA")
        total_forms = cursor.fetchone()[0]
        
        # 5. Lottery Winners (Approximate from Forms)
        cursor.execute("SELECT COUNT(*) FROM MEMBER_ESTMARA WHERE ESTMARA_FLAG = 1 OR HAVE_FLAG = 1")
        lottery_winners = cursor.fetchone()[0]

        print(f"\n[STATISTICS]")
        print(f" - Total Members in DB: {total_members:,}")
        print(f" - Contracts Made in 2026: {contracts_2026:,}")
        print(f" - Bookings Added in 2026: {bookings_2026:,}")
        print(f" - Total Forms (Estmara): {total_forms:,}")
        print(f" - Successful Lottery Entries: {lottery_winners:,}")
        
        # 6. Export Members to Excel
        print("\n[EXPORTING] Exporting all members to Excel (this may take a minute)...")
        query = """
            SELECT MEM_NO as "رقم العضوية", 
                   MEM_NAME as "الاسم الكامل", 
                   NATIONAL_NO as "الرقم القومي", 
                   TELEPHONES as "التليفون", 
                   RANK as "كود الرتبة", 
                   ADDRESS as "العنوان"
            FROM MEMBER
        """
        # Using a safer way to read sql to avoid encoding issues with pandas
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        
        output_file = "الأعضاء_الكامل_2026.xlsx"
        df.to_excel(output_file, index=False)
        print(f"[SUCCESS] Member data exported to: {output_file}")
        
        cursor.close()
        conn.close()
        
        return {
            'total_members': total_members,
            'contracts_2026': contracts_2026,
            'bookings_2026': bookings_2026,
            'total_forms': total_forms,
            'lottery_winners': lottery_winners,
            'excel_file': output_file
        }
        
    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")
        return None

if __name__ == "__main__":
    generate_report()
