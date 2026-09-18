import os
import sys
import django
import subprocess
from datetime import datetime

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")

def clear_all_data():
    """Wipes all data from the database using Django's flush command."""
    print("\n[WARNING] This will delete ALL data (bookings, units, etc.)!")
    confirm = input("Are you sure you want to proceed? (yes/no): ")
    if confirm.lower() == 'yes':
        try:
            from django.core.management import call_command
            call_command('flush', interactive=False)
            print("\n[SUCCESS] All data has been cleared.")
        except Exception as e:
            print(f"\n[ERROR] Failed to clear data: {e}")
    else:
        print("\nOperation cancelled.")

def run_backup():
    """Runs a pg_dump to create a timestamped backup."""
    db_name = os.environ.get('POSTGRES_DB', 'housing')
    db_user = os.environ.get('POSTGRES_USER', 'housing')
    db_pass = os.environ.get('POSTGRES_PASSWORD', 'housing')
    db_host = os.environ.get('POSTGRES_HOST', 'localhost')
    
    # Create backup directory
    backup_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
    if not os.path.exists(backup_root):
        os.makedirs(backup_root)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(backup_root, f"backup_{timestamp}.sql")
    
    # Find pg_dump
    pg_dump_path = None
    for d in ["C:\\Program Files\\PostgreSQL\\16\\bin\\pg_dump.exe", 
              "C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe",
              "C:\\Program Files\\PostgreSQL\\14\\bin\\pg_dump.exe"]:
        if os.path.exists(d):
            pg_dump_path = d
            break
    
    if not pg_dump_path:
        # Try generic path search
        try:
            output = subprocess.check_output(["where", "pg_dump"], shell=True).decode().strip().split('\n')[0]
            pg_dump_path = output
        except:
            print("[ERROR] pg_dump not found in common paths or PATH.")
            return

    env = os.environ.copy()
    env["PGPASSWORD"] = db_pass
    
    print(f"\nCreating backup: {backup_file} ...")
    try:
        command = [
            pg_dump_path,
            "-U", db_user,
            "-h", db_host,
            "-f", backup_file,
            db_name
        ]
        subprocess.run(command, env=env, check=True)
        print(f"[SUCCESS] Backup saved to: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Backup failed: {e}")

def schedule_backup():
    """Schedules a daily backup at 3:30 PM using Windows Task Scheduler."""
    script_path = os.path.abspath(__file__)
    python_path = sys.executable
    
    task_name = "HousingProject_DailyBackup"
    # Command to run: python db_management.py backup
    command = f'"{python_path}" "{script_path}" backup'
    
    print(f"\nScheduling daily backup at 15:30 (3:30 PM) ...")
    
    # Check if task already exists and delete it
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], capture_output=True)
    
    # Create new task
    try:
        subprocess.run([
            "schtasks", "/create", 
            "/tn", task_name, 
            "/tr", command, 
            "/sc", "daily", 
            "/st", "15:30",
            "/f"
        ], check=True)
        print(f"[SUCCESS] Daily backup scheduled successfully at 3:30 PM.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to schedule task: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python db_management.py [clear|backup|schedule]")
        sys.exit(1)
        
    action = sys.argv[1].lower()
    
    if action == "clear":
        clear_all_data()
    elif action == "backup":
        run_backup()
    elif action == "schedule":
        schedule_backup()
    else:
        print(f"Unknown action: {action}")
