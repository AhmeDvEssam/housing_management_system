import os
import sys
import django
import pandas as pd
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'housing.settings')
django.setup()

from inventory.models import Period

def parse_date(val, year=2026):
    if pd.isna(val) or val == 'nan':
        return None
    
    # If Excel already parsed it as a datetime object
    if isinstance(val, datetime):
        # The user says Excel swaps them (e.g., 8/6 in formula bar means Day 8, Month 6)
        # So we take the Excel-month as our DAY, and Excel-day as our MONTH
        try:
            # We try to swap them if both are <= 12
            if val.month <= 12 and val.day <= 12:
                return datetime(val.year, val.day, val.month).date()
            return val.date()
        except:
            return val.date()
        
    val_str = str(val).strip()
    if not val_str:
        return None
        
    # Try parsing "DD/MM" format (User's rule: Left is Day)
    try:
        if '/' in val_str:
            parts = val_str.split('/')
            # If it's a full date string like "2026-06-08" (sometimes pandas does this)
            if len(parts[0]) == 4:
                dt = datetime.strptime(val_str, "%Y-%m-%d")
                if dt.month <= 12 and dt.day <= 12:
                     return datetime(dt.year, dt.day, dt.month).date()
                return dt.date()
                
            day = int(parts[0].strip())
            month = int(parts[1].strip())
            # If there's a third part (year)
            current_year = year
            if len(parts) > 2:
                y_str = parts[2].strip()
                if len(y_str) == 4: current_year = int(y_str)
                elif len(y_str) == 2: current_year = 2000 + int(y_str)
            
            return datetime(current_year, month, day).date()
    except Exception as e:
        print(f"Failed to parse date string {val_str}: {e}")
        
    return None

def import_periods(file_path):
    print(f"Reading periods data from {file_path}")
    df = pd.read_excel(file_path)
    
    for _, row in df.iterrows():
        try:
            week_num = str(row.iloc[0]).strip()
            
            # Skip header rows
            if week_num in ('nan', 'الاسبوع', '', 'None'):
                continue
                
            name = f"الأسبوع {week_num}"
            
            start_date = parse_date(row.iloc[2])
            end_date = parse_date(row.iloc[4])
            departure_date = parse_date(row.iloc[6])
            contract_deadline = parse_date(row.iloc[8])
            
            if start_date and end_date:
                period, created = Period.objects.update_or_create(
                    name=name,
                    defaults={
                        'start_date': start_date,
                        'end_date': end_date,
                        'departure_date': departure_date,
                        'contract_deadline': contract_deadline
                    }
                )
                action = "Created" if created else "Updated"
                print(f"{action} period: {name} ({start_date} to {end_date})")
                
        except Exception as e:
            print(f"Error processing row {week_num}: {e}")

if __name__ == "__main__":
    file_path = r"d:\housing\فترات الافواج والاسابيع.xlsx"
    import_periods(file_path)
