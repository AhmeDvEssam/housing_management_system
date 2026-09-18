import oracledb

def check_oracle():
    try:
        conn = oracledb.connect(user="migration_temp", password="migration", dsn="localhost/xe")
        cursor = conn.cursor()
        
        query = """
        SELECT
            NVL((SELECT count(*)
                 FROM MEMBER_CONTRACT
                 WHERE EXTRACT(YEAR FROM RECORD_DATE) = 2025 and member_contract_flag = 1), 0)
         +
            NVL((SELECT count(*) 
                 FROM PERSON_BOOKED 
                 WHERE EXTRACT(YEAR FROM RECORD_DATE) = 2025 and person_booked_flag = 1), 0)
        AS TOTAL_SUM 
        FROM dual
        """
        cursor.execute(query)
        result = cursor.fetchone()
        print(f"Total in Oracle for 2025: {result[0]}")
        
        query1 = "SELECT count(*) FROM MEMBER_CONTRACT WHERE EXTRACT(YEAR FROM RECORD_DATE) = 2025 and member_contract_flag = 1"
        cursor.execute(query1)
        res1 = cursor.fetchone()
        print(f"MEMBER_CONTRACT in Oracle for 2025: {res1[0]}")
        
        query2 = "SELECT count(*) FROM PERSON_BOOKED WHERE EXTRACT(YEAR FROM RECORD_DATE) = 2025 and person_booked_flag = 1"
        cursor.execute(query2)
        res2 = cursor.fetchone()
        print(f"PERSON_BOOKED in Oracle for 2025: {res2[0]}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_oracle()
