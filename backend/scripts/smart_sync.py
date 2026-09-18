import os
import django
import sys
import oracledb
import json
from datetime import datetime, timedelta
import io

def safe_str(val, max_len=255):
    if val is None:
        return ""
    s = str(val).strip()
    return s[:max_len]

# Fix encoding for Arabic characters in terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from django.db import transaction, IntegrityError
from django.utils import timezone as tz
from members.models import Member, FamilyMember
from bookings.models import Booking, Contract, PersonTypeChoices, LotteryResult, BookingType
from inventory.models import Unit, Club, Building, Floor

# Oracle Connection Config
ORACLE_USER = os.environ.get('ORACLE_USER', 'MIGRATION_TEMP')
ORACLE_PASS = os.environ.get('ORACLE_PASS', 'migration')
ORACLE_DSN = os.environ.get('ORACLE_DSN', 'localhost:1521/xe')

LAST_SYNC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_sync_date.txt")
CLUB_MAP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "club_map.json")

# Default mapping if file doesn't exist
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

def load_club_map():
    if os.path.exists(CLUB_MAP_FILE):
        try:
            with open(CLUB_MAP_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CLUB_MAP.copy()

def save_club_map(m):
    with open(CLUB_MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, indent=2)

CLUB_MAP = load_club_map()

CIVILIAN_RANKS = ['19', '20', '21']

def get_oracle_conn():
    try:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            client_dir = os.path.join(base_dir, 'instantclient')
            if os.path.exists(client_dir):
                oracledb.init_oracle_client(lib_dir=client_dir)
            else:
                oracledb.init_oracle_client()
        except Exception as init_err:
            pass # Ignore if already initialized or client not found
        return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
    except Exception as e:
        print(f"[ERROR] Could not connect to Oracle: {e}")
        return None

def reset_django_db(auto_yes=False):
    print("WARNING: This will delete synced Bookings, Contracts, Companions, and Members. (Allocations and Units are kept safe).", flush=True)
    if not auto_yes:
        confirm = input("Are you sure? (y/n): ")
    else:
        confirm = 'y'
    
    if confirm.lower() == 'y':
        print("Clearing data... This may take a couple of minutes depending on database size. Please wait...", flush=True)
        from bookings.models import Companion, Booking
        
        # مسح جميع المرافقين
        Companion.objects.all().delete()
        
        # مسح جميع الحجوزات والعقود المستوردة (مع استثناء المخصصات لأنها يدوية)
        Booking.objects.exclude(booking_type='ALLOCATIONS').delete()
        
        # مسح جميع الأعضاء والتابعين
        FamilyMember.objects.all().delete()
        Member.objects.all().delete()
        
        # *لن نقوم بمسح* Unit, Floor, Building أو قواعد التسعير والأفواج للحفاظ عليها
        
        if os.path.exists(LAST_SYNC_FILE):
            os.remove(LAST_SYNC_FILE)
        print("Oracle Data cleared (Kept: Units, Floors, Buildings, Allocations, and Core Rules). Ready for full sync.", flush=True)
    else:
        print("Reset aborted.")

def get_last_sync_date(full_sync=False):
    if full_sync:
        return "2000-01-01 00:00:00"
    if os.path.exists(LAST_SYNC_FILE):
        with open(LAST_SYNC_FILE, "r") as f:
            d = f.read().strip()
            if d: return d
    return "2000-01-01 00:00:00"

def get_max_record_date(conn):
    cursor = conn.cursor()
    max_dates = []
    
    queries = [
        "SELECT MAX(RECORD_DATE) FROM MEMBER",
        "SELECT MAX(MEMBER_CONTRACT_DATE2) FROM MEMBER_CONTRACT",
        "SELECT MAX(MEMBER_CONTRACT_DATE) FROM PERSON_BOOKED",
        "SELECT MAX(RECORD_DATE) FROM SUB_MEMBER",
        "SELECT MAX(RECORD_DATE) FROM CONTRACT_COMPANY",
        "SELECT MAX(RECORD_DATE) FROM CANCELED_CONTRACT"
    ]
    
    for q in queries:
        try:
            cursor.execute(q)
            res = cursor.fetchone()
            if res and res[0]:
                max_dates.append(res[0])
        except Exception:
            pass
            
    cursor.close()
    
    if max_dates:
        return max(max_dates)
    return datetime.now()

def save_last_sync_date(conn):
    latest_date = get_max_record_date(conn)
    # Subtract a small buffer (e.g. 1 minute) just in case
    sync_val = (latest_date - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")
    with open(LAST_SYNC_FILE, "w") as f:
        f.write(sync_val)
    print(f"Updated last sync date to: {sync_val}")

def load_units_from_excel():
    import openpyxl
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'Data.xlsx')
    if not os.path.exists(excel_path):
        print(f"Excel file not found at {excel_path}. Skipping unit load.")
        return

    print("--- Loading Units from Data.xlsx using openpyxl ---")
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    ws = wb.active
    
    headers = [str(cell.value).strip() if cell.value else "" for cell in ws[1]]
    
    count_clubs, count_buildings, count_floors, count_units = 0, 0, 0, 0
    
    unit_type_map = {
        'شقة 1 غرفة': 'APARTMENT_1B',
        'شقة 2 غرفة': 'APARTMENT_2B',
        'شقة 3 غرفة': 'APARTMENT_3B',
        'شقة 1': 'APARTMENT_1B',
        'شقة 2': 'APARTMENT_2B',
        'شقة 3': 'APARTMENT_3B',
        'شقة': 'APARTMENT_2B',
        'غرفة': 'ROOM',
        'غرفه': 'ROOM',
        'جناح': 'SUITE',
        'فيلا': 'VILLA',
    }

    def get_capacity(utype):
        if utype == 'APARTMENT_1B': return 2
        if utype == 'APARTMENT_2B': return 4
        if utype == 'APARTMENT_3B': return 6
        if utype == 'SUITE': return 4
        if utype == 'ROOM': return 2
        if utype == 'VILLA': return 6
        return 2

    for row_idx, row_cells in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        row_list = list(row_cells)
        club_name = str(row_list[0]).strip() if len(row_list) > 0 and row_list[0] is not None else ''
        build_name = str(row_list[1]).strip() if len(row_list) > 1 and row_list[1] is not None else ''
        flat_id = str(row_list[2]).strip() if len(row_list) > 2 and row_list[2] is not None else ''
        unit_no = str(row_list[3]).strip() if len(row_list) > 3 and row_list[3] is not None else ''
        unit_type_raw = str(row_list[4]).strip() if len(row_list) > 4 and row_list[4] is not None else ''
        classification = str(row_list[5]).strip() if len(row_list) > 5 and row_list[5] is not None else ''
        floor_name = str(row_list[6]).strip() if len(row_list) > 6 and row_list[6] is not None else ''
        allocation = '' # Index 7 removed
        
        if classification == 'nan': classification = ''
        if allocation == 'nan': allocation = ''
        if flat_id == 'nan' or flat_id == 'None': flat_id = ''
        
        # Combine flat_id and allocation into notes
        notes_val = f"[FLAT_ID:{flat_id}] {allocation}".strip() if flat_id else f"{allocation}".strip()
        
        if not club_name or not build_name or not unit_no or unit_no == 'nan':
            continue
            
        club, created_c = Club.objects.get_or_create(
            name=club_name,
            defaults={'city': 'غير محدد'}
        )
        if created_c: count_clubs += 1
        
        building, created_b = Building.objects.get_or_create(
            club=club,
            name=build_name
        )
        if created_b: count_buildings += 1
        
        level = 1
        if 'ارضي' in floor_name or 'أرضي' in floor_name: level = 0
        elif 'اول' in floor_name or 'أول' in floor_name: level = 1
        elif 'ثاني' in floor_name or 'تاني' in floor_name or 'ثانى' in floor_name: level = 2
        elif 'ثالث' in floor_name or 'تالت' in floor_name: level = 3
        elif 'رابع' in floor_name: level = 4
        elif 'خامس' in floor_name: level = 5
        elif 'سادس' in floor_name: level = 6
        elif 'سابع' in floor_name: level = 7
        elif 'ثامن' in floor_name: level = 8
        elif 'تاسع' in floor_name: level = 9
        elif 'عاشر' in floor_name: level = 10
        
        floor, created_f = Floor.objects.get_or_create(
            building=building,
            label=floor_name,
            defaults={'level_number': level}
        )
        # Update level if it changed or wasn't set
        if not created_f and floor.level_number != level:
            floor.level_number = level
            floor.save()
        if created_f: count_floors += 1
        
        mapped_type = 'APARTMENT_1B'
        for k, v in unit_type_map.items():
            if k in unit_type_raw:
                mapped_type = v
                break
        
        unit, created_u = Unit.objects.update_or_create(
            floor=floor,
            unit_no=unit_no,
            defaults={
                'unit_type': mapped_type,
                'classification': classification,
                'is_bookable': True,
                'capacity': get_capacity(mapped_type),
                'notes': notes_val
            }
        )
        if created_u: count_units += 1

    print(f"Loaded {count_units} units across {count_clubs} clubs from Excel.")

def get_unit_from_our_db(club_id, unit_no, flat_id=None):
    if flat_id:
        # Try exact match using flat_id saved in notes
        unit = Unit.objects.filter(notes__contains=f"[FLAT_ID:{flat_id}]").first()
        if unit:
            return unit

    # Fallback to old behavior (match by club and flat_num)
    club_name = CLUB_MAP.get(str(club_id))
    if not club_name: return None
    clean_unit_no = str(unit_no).strip()
    return Unit.objects.filter(floor__building__club__name=club_name, unit_no=clean_unit_no).first()

def smart_sync_members(conn, last_sync):
    print("\n--- Syncing Members (MEMBER) ---", flush=True)
    print("> Fetching data from Oracle... please wait.", flush=True)
    cursor = conn.cursor()
    if last_sync == "2000-01-01 00:00:00":
        query = "SELECT MEM_NO, MEM_NAME, NATIONAL_NO, TELEPHONES, RANK, ADDRESS, MEM_MIL_NO FROM MEMBER"
    else:
        query = f"SELECT MEM_NO, MEM_NAME, NATIONAL_NO, TELEPHONES, RANK, ADDRESS, MEM_MIL_NO FROM MEMBER WHERE RECORD_DATE >= TO_DATE('{last_sync}', 'YYYY-MM-DD HH24:MI:SS')"

    RANK_MAP = {
        '1': 'طالب', '2': 'عريف', '3': 'رقيب', '4': 'رقيب اول',
        '5': 'مســـاعد', '6': 'مساعد اول', '7': 'صانع', '8': 'صانع دقيق',
        '9': 'ملاحظ فنى', '10': 'صانع ماهر', '11': 'صانع ممتاز',
        '12': 'ملازم', '13': 'ملازم اول', '14': 'نقيب', '15': 'رائـــد',
        '16': 'مقدم', '17': 'جنـــدى', '18': 'طالبة',
        '19': 'مدنى', '20': 'مدنية', '21': 'مدني*'
    }

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        total = len(rows)
        print(f"> Got {total} members from Oracle. Now saving to Django DB...", flush=True)
        count, skipped = 0, 0
        for i, row in enumerate(rows, 1):
            mem_no, mem_name, nat_no, telephones, rank, addr, mil_no = row
            if not mem_no: continue
            
            rank_str = str(rank) if rank else ""
            rank_name = RANK_MAP.get(rank_str, rank_str)
            is_civilian = rank_str in CIVILIAN_RANKS
            
            _, created = Member.objects.update_or_create(
                membership_no=str(mem_no),
                defaults={
                    'full_name': str(mem_name)[:200] if mem_name else "بدون اسم",
                    'national_id': str(nat_no)[:14] if nat_no else "",
                    'phone': str(telephones)[:20] if telephones else "",
                    'rank': rank_name,
                    'job_type': "مدني" if is_civilian else "عسكري",
                    'address': str(addr)[:255] if addr else "",
                    'notes': f"رقم عسكري: {mil_no}" if mil_no else ""
                }
            )
            if created: count += 1
            else: skipped += 1
            if i % 500 == 0:
                print(f"  ... {i}/{total} members processed ({count} new, {skipped} updated)", flush=True)
            
        print(f"[SUCCESS] Members: {count} new, {skipped} updated.", flush=True)
    except Exception as e:
        print(f"[ERROR] Member sync failed: {e}", flush=True)
    finally:
        cursor.close()

def smart_sync_sub_members(conn, last_sync):
    print("\n--- Syncing Family Members (SUB_MEMBER) ---", flush=True)
    print("> Fetching family members from Oracle...", flush=True)
    cursor = conn.cursor()
    
    if last_sync == "2000-01-01 00:00:00":
        query = "SELECT MEM_NO, MEM_NAME, RELATION_ID FROM SUB_MEMBER"
    else:
        query = f"SELECT MEM_NO, MEM_NAME, RELATION_ID FROM SUB_MEMBER WHERE RECORD_DATE >= TO_DATE('{last_sync}', 'YYYY-MM-DD HH24:MI:SS')"
        
    RELATION_MAP = {'1': 'زوجة', '2': 'ابن', '3': 'ابنة', '4': 'أب', '5': 'أم', '6': 'أخ', '7': 'أخت'}
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        total = len(rows)
        print(f"> Got {total} family members from Oracle. Now saving...", flush=True)
        
        count = 0
        for i, (mem_no, name, rel_id) in enumerate(rows, 1):
            if not mem_no or not name: continue
            
            member = Member.objects.filter(membership_no=str(mem_no)).first()
            if not member: continue
            
            rel_str = str(rel_id) if rel_id else ""
            rel_name = RELATION_MAP.get(rel_str, "فرد عائلة")
            
            _, created = FamilyMember.objects.get_or_create(
                member=member,
                name=str(name).strip()[:200],
                defaults={'relation': rel_name}
            )
            if created: count += 1
            if i % 500 == 0:
                print(f"  ... {i}/{total} family members processed", flush=True)
            
        print(f"[SUCCESS] Family Members: {count} added.", flush=True)
    except Exception as e:
        print(f"[ERROR] SUB_MEMBER sync failed: {e}", flush=True)
    finally:
        cursor.close()

def smart_sync_contracts(conn, last_sync):
    global skipped_records
    skipped_records = []
    print("\n--- Syncing Contracts (MEMBER_CONTRACT) ---", flush=True)
    print("> Fetching contracts from Oracle...", flush=True)
    cursor = conn.cursor()
    
    CONTRACT_TYPE_TO_ARMY = {
        1: 'المنطقة المركزية', 2: 'الجيش الثاني الميداني', 3: 'الجيش الثالث الميداني',
        4: 'المنطقة الشمالية', 5: 'المنطقة الغربية', 6: 'المنطقة الجنوبية',
        7: 'القوات البحرية', 8: 'القوات الجوية', 10: 'قوات الدفاع الجوى',
        11: 'حرس الحدود', 12: 'قوات الصاعقة', 13: 'قوات المظلات',
        14: 'الدفاع الشعبى', 15: 'قوات شرق القناة', 16: 'حرس جمهورى',
        17: 'هيئة تنظيم وادارة', 20: 'جهة أخرى'
    }

    club_ids = tuple(int(k) for k in CLUB_MAP.keys())
    
    date_filter = ""
    if last_sync != "2000-01-01 00:00:00":
        date_filter = f"AND mc.MEMBER_CONTRACT_DATE2 >= TO_DATE('{last_sync}', 'YYYY-MM-DD HH24:MI:SS')"

    query = f"""
        SELECT mc.MEM_NO, mc.FLAT_ID, mc.FOR_YEAR, mc.FROM_DATE, mc.TO_DATE, mc.MEMBER_CONTRACT_VAL3, mc.MEMBER_CONTRACT_NUM3, f.PLA_CODE, f.FLAT_NUM, mc.MEMBER_CONTRACT_FLAG, mc.START_FTRA_DATE, mc.END_FTRA_DATE, mc.MEMBER_CONTRACT_TYPE, mc.MEMBER_CONTRACT_DATE2, mc.PAY_METHOD
        FROM MEMBER_CONTRACT mc
        JOIN FLAT f ON mc.FLAT_ID = f.FLAT_ID
        WHERE f.PLA_CODE IN {club_ids} {date_filter}
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        total = len(rows)
        print(f"> Got {total} contracts from Oracle. Now saving...", flush=True)
        
        count, skipped, no_mem, no_unit = 0, 0, 0, 0
        for i, row in enumerate(rows, 1):
            mem_no, flat_id, year, start, end, val, cont_num, club_id, flat_num, contract_flag, start_first, end_last, contract_type, rec_date, pay_method = row
            start = start_first
            end = end_last
            if not start or not end: continue
            
            member = Member.objects.filter(membership_no=str(mem_no)).first()
            if not member:
                no_mem += 1
                continue
                
            unit = get_unit_from_our_db(club_id, flat_num, flat_id)
            if not unit:
                no_unit += 1
                continue
                
            person_type = PersonTypeChoices.FAMILY_MEMBER if member.rank in ['مدنى', 'مدنية', 'مدني*'] else PersonTypeChoices.MILITARY
            b_status = "مؤكد" if str(contract_flag) == "1" else "غير مؤكد"
            
            start_date = start.date() if hasattr(start, 'date') else start
            end_date = end.date() if hasattr(end, 'date') else end
            
            # The database stores the last night for MEMBER_CONTRACT. We need the departure date (last night + 1 day).
            try:
                end_date = end_date + timedelta(days=1)
            except TypeError:
                # Fallback if end_date is somehow not a date object
                pass
            
            if contract_type == 9:
                b_type = BookingType.LOTTERY
                army_region_val = ""
            else:
                b_type = BookingType.ARMIES_REGIONS
                army_region_val = CONTRACT_TYPE_TO_ARMY.get(contract_type, "جهة أخرى (غير محددة)")

            try:
                with transaction.atomic():
                    guest_name_val = member.full_name
                    guest_id_val = member.membership_no
                    
                    b, created = Booking.objects.get_or_create(
                        member=member,
                        unit=unit,
                        start_date=start_date,
                        end_date=end_date,
                        defaults={
                            'guest_id_no': guest_id_val,
                            'guest_name': guest_name_val,
                            'total_price': float(val) if val else 0,
                            'status': b_status,
                            'booking_type': b_type,
                            'contract_no': str(cont_num) if cont_num else "",
                            'person_type': person_type,
                            'army_region': army_region_val,
                            'record_date': tz.make_aware(rec_date) if rec_date and not tz.is_aware(rec_date) else rec_date,
                            'pay_method': int(pay_method) if pay_method else 0
                        }
                    )
                    b._skip_booking_days = True
                    if created:
                        b.save()
                        count += 1
                    else:
                        # Update status and record_date (important for lottery payments)
                        b.status = b_status
                        if rec_date:
                            b.record_date = tz.make_aware(rec_date) if not tz.is_aware(rec_date) else rec_date
                        b.save()
                        skipped += 1
            except Exception as e:
                skipped += 1
            if i % 500 == 0:
                print(f"  ... {i}/{total} contracts processed ({count} new, {skipped} skipped)", flush=True)
        print(f"[SUCCESS] Contracts: {count} new, {skipped} updated/skipped, {no_mem} no member, {no_unit} no unit.", flush=True)
    except Exception as e:
        print(f"[ERROR] Contract sync failed: {e}", flush=True)
    finally:
        cursor.close()

skipped_records = []

def smart_sync_bookings(conn, last_sync):
    global skipped_records
    skipped_records = []
    print("--- Syncing Bookings (PERSON_BOOKED) ---", flush=True)
    print("> Fetching bookings from Oracle...", flush=True)
    cursor = conn.cursor()
    
    # PERSON_BOOKED contains other bookings
    club_ids = tuple(int(k) for k in CLUB_MAP.keys())
        
    date_filter = ""
    if last_sync != "2000-01-01 00:00:00":
        date_filter = f"AND pb.MEMBER_CONTRACT_DATE >= TO_DATE('{last_sync}', 'YYYY-MM-DD HH24:MI:SS')"

    query = f"""
        SELECT pb.MEM_NO, pb.PERSON_NAME, pb.MEMBER_CONTRACT_DATE, pb.DAYS_NUMBER, f.PLA_CODE, pb.BOOKING_NUM, f.FLAT_NUM, pb.PERSON_TYPE, pb.BOOKED_START, pb.BOOKED_END, pb.PERSON_BOOKED_FLAG, pb.CANCELLATION_DATE, pb.PAYMENT_METHOD, pb.MEMBER_CONTRACT_VAL, f.FLAT_ID
        FROM PERSON_BOOKED pb
        JOIN FLAT f ON pb.FLAT_ID = f.FLAT_ID
        WHERE f.PLA_CODE IN {club_ids} {date_filter}
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        total = len(rows)
        print(f"> Got {total} bookings from Oracle. Now saving...", flush=True)
        
        count = 0
        skipped = 0
        no_unit = 0
        for i, row in enumerate(rows, 1):
            mem_no, person_name, rec_date, days, club_id, book_num, flat_num, p_type, booked_start, booked_end, booked_flag, cancel_date, pay_method, total_val, flat_id = row
            
            member = Member.objects.filter(membership_no=str(mem_no)).first()
            
            # Fetch the actual unit
            unit = get_unit_from_our_db(club_id, flat_num, flat_id)
            if not unit:
                no_unit += 1
                continue

            start = booked_start.date() if hasattr(booked_start, 'date') else booked_start
            if not start: continue
            end = booked_end.date() if hasattr(booked_end, 'date') else booked_end
            
            # Person type
            person_type_map = {
                '1': PersonTypeChoices.CIVILIAN_GENERAL,
                '2': PersonTypeChoices.CIVILIAN_AF,
                '3': PersonTypeChoices.MARTYR,
                '4': PersonTypeChoices.MILITARY,
                '5': PersonTypeChoices.FAMILY_MEMBER,
            }
            if p_type and str(p_type) in person_type_map:
                person_type = person_type_map[str(p_type)]
            else:
                if not member:
                    person_type = PersonTypeChoices.CIVILIAN_GENERAL
                elif member.rank in ['مدنى', 'مدنية', 'مدني*']:
                    person_type = PersonTypeChoices.FAMILY_MEMBER
                else:
                    person_type = PersonTypeChoices.MILITARY

            guest_name_val = str(person_name)[:200] if person_name else (member.full_name if member else f"ضيف غير مسجل ({mem_no})")
            guest_id_val = str(mem_no) if mem_no else ""
            
            # Map person_type to guest_rank so it displays correctly in the UI
            guest_rank_val = ""
            if member and member.rank:
                guest_rank_val = member.rank
            else:
                guest_rank_val = dict(PersonTypeChoices.choices).get(person_type, "")

            # Booking status logic (1 = مؤكد, 0 = غير مؤكد)
            if cancel_date:
                b_status = "ملغي"
            else:
                b_status = "مؤكد" if str(booked_flag) == "1" else "غير مؤكد"
            
            b_type = BookingType.STANDARD
                
            try:
                with transaction.atomic():
                    # 1. Check if there is an overlapping contract booking for the same member and unit
                    existing_contract = None
                    if member:
                        existing_contract = Booking.objects.filter(
                            member=member,
                            unit=unit,
                            start_date__lte=start,
                            end_date__gte=end
                        ).first()
                        
                    if existing_contract:
                        # Merge! Update dates to the actual physical booking dates
                        existing_contract.start_date = start
                        existing_contract.end_date = end
                        existing_contract.guest_name = guest_name_val
                        existing_contract.guest_rank = guest_rank_val
                        existing_contract.person_type = person_type
                        existing_contract.status = b_status
                        existing_contract.record_date = tz.make_aware(rec_date) if rec_date and not tz.is_aware(rec_date) else rec_date
                        if total_val: existing_contract.total_price = float(total_val)
                        if pay_method: existing_contract.pay_method = int(pay_method)
                        existing_contract._skip_booking_days = True
                        existing_contract.save()
                        count += 1
                        continue

                    # 2. Check if this exact booking already exists (skip duplicates)
                    existing = Booking.objects.filter(
                        unit=unit,
                        start_date=start,
                        end_date=end
                    ).first()
                    if existing:
                        existing.record_date = tz.make_aware(rec_date) if rec_date and not tz.is_aware(rec_date) else rec_date
                        existing.pay_method = int(pay_method) if pay_method else 0
                        existing.guest_rank = guest_rank_val
                        existing.person_type = person_type
                        if total_val: existing.total_price = float(total_val)
                        existing._skip_booking_days = True
                        existing.save()
                        skipped += 1
                        skipped_records.append({
                            'Type': 'Civilian',
                            'Oracle Name': guest_name_val,
                            'DB Name': existing.guest_name,
                            'Unit': existing.unit.unit_no,
                            'Start Date': start,
                            'End Date': end
                        })
                        continue
                    
                    b = Booking(
                        guest_name=guest_name_val,
                        guest_id_no=guest_id_val,
                        guest_rank=guest_rank_val,
                        start_date=start,
                        end_date=end,
                        unit=unit,
                        member=member,
                        status=b_status,
                        booking_type=b_type,
                        person_type=person_type,
                        record_date=tz.make_aware(rec_date) if rec_date and not tz.is_aware(rec_date) else rec_date,
                        total_price=float(total_val) if total_val else 0,
                        pay_method=int(pay_method) if pay_method else 0
                    )
                    # Bypass BookingDay creation for non-standard overlapping slots
                    b._skip_booking_days = True
                    b.save()
                    count += 1
            except (IntegrityError, Exception) as e:
                print(f"Skipped PERSON_BOOKED record due to: {e}", flush=True)
                skipped += 1
                continue
            if i % 500 == 0:
                print(f"  ... {i}/{total} bookings processed ({count} new, {skipped} skipped)", flush=True)
        print(f"[SUCCESS] Person Bookings: {count} new, {skipped} skipped (duplicates), {no_unit} no unit match.", flush=True)
    except Exception as e:
        print(f"[ERROR] Person booked sync failed: {e}", flush=True)
    finally:
        cursor.close()


def smart_sync_companions(conn, last_sync):
    print("--- Syncing Companions (CONTRACT_COMPANY) ---")
    cursor = conn.cursor()
    
    from bookings.models import Companion
    club_ids = tuple(int(k) for k in CLUB_MAP.keys())
        
    date_filter = ""
    if last_sync != "2000-01-01 00:00:00":
        date_filter = f"AND cc.RECORD_DATE >= TO_DATE('{last_sync}', 'YYYY-MM-DD HH24:MI:SS')"

    query = f"""
        SELECT cc.NAME, cc.START_FTRA_DATE, f.FLAT_NUM, f.PLA_CODE, cc.RECORD_DATE
        FROM CONTRACT_COMPANY cc
        JOIN FLAT f ON cc.FLAT_ID = f.FLAT_ID
        WHERE f.PLA_CODE IN {club_ids} {date_filter}
    """
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        print(f"Processing {len(rows)} companions...")
        
        count = 0
        skipped = 0
        no_booking = 0
        
        for row in rows:
            name, start_ftra, flat_num, club_id, rec_date = row
            if not name: continue
            
            unit = get_unit_from_our_db(club_id, flat_num)
            if not unit:
                continue
                
            start_date = start_ftra.date() if hasattr(start_ftra, 'date') else start_ftra
            if not start_date: continue
            
            # Find the booking for this unit covering the period
            booking = Booking.objects.filter(
                unit=unit,
                start_date__lte=start_date,
                end_date__gte=start_date
            ).first()
            
            if not booking:
                no_booking += 1
                continue
                
            companion_name = str(name).strip()
            
            # Check if companion already linked
            existing = Companion.objects.filter(booking=booking, name=companion_name).exists()
            if existing:
                skipped += 1
                continue
                
            c = Companion(
                booking=booking,
                name=companion_name
            )
            c._skip_price_update = True
            c.save()
            count += 1
            
        print(f"[SUCCESS] Companions: {count} synced, {skipped} skipped (duplicates), {no_booking} bookings not found.")
    except Exception as e:
        print(f"[ERROR] Companion sync failed: {e}")
    finally:
        cursor.close()

def smart_sync_cancellations(conn, last_sync):
    print("\n--- Syncing Cancellations (CANCELED_CONTRACT) ---")
    cursor = conn.cursor()
    # Check if table exists
    try:
        cursor.execute("SELECT COUNT(*) FROM CANCELED_CONTRACT")
        if cursor.fetchone()[0] == 0:
            print("No cancellations found in Oracle.")
            return
            
        club_ids = tuple(int(k) for k in CLUB_MAP.keys())
        
        date_filter = ""
        if last_sync != "2000-01-01 00:00:00":
            date_filter = f"AND cc.RECORD_DATE >= TO_DATE('{last_sync}', 'YYYY-MM-DD HH24:MI:SS')"
            
        query = f"""
            SELECT cc.MEM_NO, cc.START_FTRA_DATE, f.PLA_CODE, f.FLAT_NUM
            FROM CANCELED_CONTRACT cc
            JOIN FLAT f ON cc.FLAT_ID = f.FLAT_ID
            WHERE f.PLA_CODE IN {club_ids} {date_filter}
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        count = 0
        for mem_no, start_ftra, club_id, flat_num in rows:
            start = start_ftra
            if not start: continue
            start_date = start.date() if hasattr(start, 'date') else start
            
            unit = get_unit_from_our_db(club_id, flat_num)
            if not unit: continue
            
            # Find and cancel booking
            bookings = Booking.objects.filter(
                member__membership_no=str(mem_no),
                unit=unit,
                start_date=start_date
            )
            for b in bookings:
                if b.status != "ملغي":
                    b.status = "ملغي"
                    b.save()
                    count += 1
                    
        print(f"[SUCCESS] Cancelled {count} bookings based on CANCELED_CONTRACT.")
    except Exception as e:
        print(f"[ERROR] Cancellation sync failed: {e}")
    finally:
        cursor.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Smart Data Sync Tool')
    parser.add_argument('--full', action='store_true', help='Force a full sync ignoring last sync date')
    parser.add_argument('--reset', action='store_true', help='Clear Django db (Bookings/Members) and do full sync from Oracle.')
    parser.add_argument('--reset-units', action='store_true', help='Wipe ONLY Units and Bookings, reload from Data.xlsx, and do full sync. Keeps Members/Prices safe.')
    parser.add_argument('--yes', action='store_true', help='Auto-answer yes to prompts.')
    parser.add_argument('--skip-members', action='store_true', help='Skip syncing members and family members')
    parser.add_argument('--ignore-missing', action='store_true', help='Do not ask to add missing units, just skip them')
    args = parser.parse_args()
    
    if args.reset:
        reset_django_db(auto_yes=args.yes)
        
    if args.reset_units:
        print("\n[SYNC UNITS] Reloading/Updating units from Data.xlsx (Bookings and Members are kept safe)...", flush=True)
        load_units_from_excel()
        print("\n[SUCCESS] Unit Sync Completed successfully. Skipping Oracle sync for Bookings/Members.")
        import sys
        sys.exit(0)
    
    import time
    import datetime
    import subprocess
    import json

    def get_system_load_recommendation():
        try:
            out_cpu = subprocess.check_output('powershell -c "Get-CimInstance Win32_Processor | Select-Object LoadPercentage | ConvertTo-Json"', shell=True).decode()
            cpu_data = json.loads(out_cpu)
            cpu = float(cpu_data.get('LoadPercentage', 20.0))
        except Exception:
            cpu = 20.0
            
        try:
            out_mem = subprocess.check_output('powershell -c "Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory,TotalVisibleMemorySize | ConvertTo-Json"', shell=True).decode()
            mem_data = json.loads(out_mem)
            free = float(mem_data.get('FreePhysicalMemory', 0))
            total = float(mem_data.get('TotalVisibleMemorySize', 1))
            mem = 100.0 * (1.0 - (free / total))
        except Exception:
            mem = 40.0

        if cpu > 80 or mem > 85:
            rec = 300
        elif cpu > 50 or mem > 70:
            rec = 120
        else:
            rec = 30
        return rec, cpu, mem

    if args.full or args.reset:
        loop_mode = False
        delay_seconds = 0
        custom_date = ""
    else:
        print("\n=== Auto Sync Settings ===")
        rec_time, cpu_load, mem_load = get_system_load_recommendation()
        print(f"System Status -> CPU: {cpu_load:.1f}% | RAM: {mem_load:.1f}%")
        print(f"Recommended Delay: {rec_time} seconds")
        
        user_delay = input(f"Enter delay time in seconds (Press Enter to use recommended {rec_time}s, or 0 to run once): ").strip()
        if user_delay == "0":
            loop_mode = False
            delay_seconds = 0
        else:
            loop_mode = True
            delay_seconds = int(user_delay) if user_delay.isdigit() else rec_time
        
        print(f"\nLast recorded sync is: {get_last_sync_date(False)}")
        custom_date = input("Enter a custom Start Date 'YYYY-MM-DD HH:MM:SS' (or press Enter to use the last sync date): ").strip()

    while True:
        conn = get_oracle_conn()
        if conn:
            try:
                if custom_date:
                    last_sync = custom_date
                else:
                    last_sync = get_last_sync_date(full_sync=args.full or args.reset)
                    
                print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting sync from: {last_sync}")
                
                if not args.skip_members:
                    smart_sync_members(conn, last_sync)
                    smart_sync_sub_members(conn, last_sync)
                else:
                    print("\n--- Skipping Members and Family Members Sync ---")
                
                smart_sync_contracts(conn, last_sync)
                smart_sync_bookings(conn, last_sync)
                smart_sync_companions(conn, last_sync)
                smart_sync_cancellations(conn, last_sync)
                

                # Write skipped records to Excel using openpyxl
                if skipped_records:
                    import openpyxl
                    from openpyxl import Workbook
                    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
                    os.makedirs(log_dir, exist_ok=True)
                    log_file = os.path.join(log_dir, 'skipped_bookings.xlsx')
                    
                    if os.path.exists(log_file):
                        wb = openpyxl.load_workbook(log_file)
                        ws = wb.active
                    else:
                        wb = Workbook()
                        ws = wb.active
                        ws.append(['Type', 'Oracle Name', 'DB Name', 'Unit', 'Start Date', 'End Date'])
                        
                    for rec in skipped_records:
                        ws.append([rec.get('Type'), rec.get('Oracle Name'), rec.get('DB Name'), rec.get('Unit'), str(rec.get('Start Date')), str(rec.get('End Date'))])
                        
                    wb.save(log_file)
                    print(f"\n[INFO] Saved {len(skipped_records)} skipped bookings to {log_file}")
                    skipped_records = []
                
                save_last_sync_date(conn)
                print(f"\n[SUCCESS] Smart Sync Completed at {datetime.datetime.now().strftime('%H:%M:%S')}.")
            except Exception as e:
                print(f"\n[ERROR] An error occurred during sync: {e}")
            finally:
                conn.close()
        else:
            print("\n[FAILED] Sync could not start - Oracle connection failed.")
            
        if not loop_mode:
            break
            
        print(f"\nWaiting for {delay_seconds} seconds before next sync... (Press Ctrl+C to stop)")
        try:
            time.sleep(delay_seconds)
            # Clear custom_date after first run if we want subsequent runs to use the newly saved sync date
            custom_date = ""
        except KeyboardInterrupt:
            print("\nSync loop stopped by user.")
            break