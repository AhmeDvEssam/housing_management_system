import os, django, sys, oracledb
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
sys.path.append('backend')
django.setup()
from bookings.models import Booking
from django.db import transaction

ORACLE_USER = 'MIGRATION_TEMP'
ORACLE_PASS = 'migration'
ORACLE_DSN = 'localhost:1521/xe'

def update_prices():
    conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    cur = conn.cursor()
    
    print("Updating MEMBER_CONTRACT...")
    cur.execute("SELECT MEM_NO, FLAT_ID, FROM_DATE, MEMBER_CONTRACT_VAL3, PAY_METHOD, RECORD_DATE FROM MEMBER_CONTRACT")
    rows = cur.fetchall()
    with transaction.atomic():
        for mem_no, flat_id, start, val, pay_method, rec_date in rows:
            if not start: continue
            start_date = start.date() if hasattr(start, 'date') else start
            pay = int(pay_method) if pay_method in [0,1,2,'0','1','2'] else 0
            Booking.objects.filter(member__membership_no=str(mem_no), start_date=start_date).update(total_price=val or 0, pay_method=pay, record_date=rec_date)
            
    print("Updating PERSON_BOOKED...")
    cur.execute("SELECT MEM_NO, BOOKED_START, FLAT_ID, MEMBER_CONTRACT_VAL, RENT_VAL, INSURANCE_VAL, PAYMENT_METHOD, RECORD_DATE FROM PERSON_BOOKED")
    rows2 = cur.fetchall()
    with transaction.atomic():
        for mem_no, start, flat_id, pb_val, pb_rent, pb_insur, pb_pay, rec_date in rows2:
            if not start: continue
            start_date = start.date() if hasattr(start, 'date') else start
            val = float(pb_val or 0) + float(pb_rent or 0) + float(pb_insur or 0)
            pay = int(pb_pay) if pb_pay in [0,1,2,'0','1','2'] else 0
            
            # Find the booking by flat ID (from mapping) and date
            if mem_no:
                Booking.objects.filter(member__membership_no=str(mem_no), start_date=start_date).update(total_price=val, pay_method=pay, record_date=rec_date)
            else:
                Booking.objects.filter(start_date=start_date, person_type='CIVILIAN_GENERAL').update(total_price=val, pay_method=pay, record_date=rec_date)

            
    conn.close()
    print("Prices updated successfully.")

if __name__ == '__main__':
    update_prices()
