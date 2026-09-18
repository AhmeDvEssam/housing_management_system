import os
import sys
import oracledb
import pandas as pd
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

def export_contracts():
    print("Connecting to database...")
    try:
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
        cursor = conn.cursor()
        
        print("Extracting data from MEMBER_CONTRACT...")
        # Get all contracts, but order them so 2026 is prominent or just get everything
        query = """
            SELECT mc.*, f.FLAT_NUM
            FROM MEMBER_CONTRACT mc
            LEFT JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [col[0] for col in cursor.description]
        
        df = pd.DataFrame(rows, columns=cols)
        
        print(f"Total rows extracted: {len(df)}")
        
        # Check 2026 data
        df_2026 = df[df['FOR_YEAR'] == 2026]
        print(f"Rows for year 2026: {len(df_2026)}")
        
        output_file = r"d:\housing\MEMBER_CONTRACT_ALL.xlsx"
        print(f"Saving to Excel: {output_file}")
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        print("Done successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    export_contracts()
