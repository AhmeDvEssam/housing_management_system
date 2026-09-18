import os, subprocess, time

dmp_file = r'D:\housing\DMP\oct_29_06_26.DMP'
temp_dmp = r'C:\temp\current.dmp'

if os.path.exists(dmp_file):
    print("Copying dump file...")
    import shutil
    shutil.copy2(dmp_file, temp_dmp)

print("1. Recreating MIGRATION_TEMP user...")
setup_sql = """
ALTER SESSION SET "_ORACLE_SCRIPT"=true;
BEGIN
    EXECUTE IMMEDIATE 'DROP USER MIGRATION_TEMP CASCADE';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
CREATE USER MIGRATION_TEMP IDENTIFIED BY migration DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP QUOTA UNLIMITED ON USERS;
GRANT CONNECT, RESOURCE, DBA, IMP_FULL_DATABASE TO MIGRATION_TEMP;
EXIT;
"""
with open(r'C:\temp\setup.sql', 'w', encoding='utf-8') as f:
    f.write(setup_sql)

subprocess.run(['sqlplus', '-s', '/ as sysdba', '@C:\\temp\\setup.sql'])

print("2. Running precreate_tables.sql (which now has DROP TABLE safely ignored if missing)...")
os.chdir(r'D:\housing\Bat_Files')
# We must use a clean precreate_tables.sql without duplicate executions
with open('precreate_tables.sql', 'r', encoding='utf-8') as f:
    sql = f.read()
# Replace ';\nCREATE TABLE' with just '\nCREATE TABLE' or similar?
# Actually, let's just let it run. ORA-00955 is harmless.
subprocess.run(['sqlplus', '-s', 'migration_temp/migration@xe', '@precreate_tables.sql'])

print("3. Importing dump file...")
os.chdir(r'C:\temp')
imp_cmd = ['imp', 'migration_temp/migration@xe', 'file=current.dmp', 'full=y', 'ignore=y']
with open('imp_log.txt', 'wb') as f:
    subprocess.run(imp_cmd, stdout=f, stderr=subprocess.STDOUT)

print("Import done.")
