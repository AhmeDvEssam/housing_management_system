import os, subprocess

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

print("1. Recreating MIGRATION_TEMP user...")
subprocess.run(['sqlplus', '-s', '/ as sysdba', '@C:\\temp\\setup.sql'])

print("2. Running precreate_tables.sql...")
# We must use the 8.3 short path or chdir to the directory to avoid unicode issues with sqlplus
os.chdir(r'D:\housing\Bat_Files')
subprocess.run(['sqlplus', '-s', 'migration_temp/migration@xe', '@precreate_tables.sql'])

print("3. Running Oracle Import...")
os.chdir(r'D:\housing\DMP')
imp_cmd = [
    'imp', 'migration_temp/migration@xe',
    'file=oct_29_06_26.DMP',
    'full=y', 'ignore=y'
]
with open(r'D:\housing\imp_output.txt', 'wb') as f:
    p = subprocess.Popen(imp_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    f.write(out)

print("Oracle Import done. Output saved to imp_output.txt")
