import os, subprocess

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
with open(r'C:\temp\setup.sql', 'w') as f:
    f.write(setup_sql)

subprocess.run(['sqlplus', '-s', '/ as sysdba', '@C:\\temp\\setup.sql'])

print("2. Running precreate_tables.sql...")
subprocess.run(['sqlplus', '-s', 'migration_temp/migration@xe', '@D:\\housing\\Bat_Files\\precreate_tables.sql'])

print("3. Running Oracle Import...")
imp_cmd = [
    'imp', 'migration_temp/migration@xe',
    r'file=D:\housing\DMP\oct_29_06_26.DMP',
    'full=y', 'ignore=y'
]
with open(r'D:\housing\imp_output.txt', 'w') as f:
    subprocess.run(imp_cmd, stdout=f, stderr=subprocess.STDOUT)

print("Oracle Import done. Output saved to imp_output.txt")
