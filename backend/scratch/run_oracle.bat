@echo off
chcp 65001 >nul

echo 1. Recreating MIGRATION_TEMP user...
(
echo ALTER SESSION SET "_ORACLE_SCRIPT"=true;
echo BEGIN
echo     EXECUTE IMMEDIATE 'DROP USER MIGRATION_TEMP CASCADE';
echo EXCEPTION WHEN OTHERS THEN NULL;
echo END;
echo /
echo CREATE USER MIGRATION_TEMP IDENTIFIED BY migration DEFAULT TABLESPACE USERS TEMPORARY TABLESPACE TEMP QUOTA UNLIMITED ON USERS;
echo GRANT CONNECT, RESOURCE, DBA, IMP_FULL_DATABASE TO MIGRATION_TEMP;
echo EXIT;
) > "C:\temp\setup.sql"
sqlplus -s / as sysdba @"C:\temp\setup.sql"

echo 2. Running precreate_tables.sql...
sqlplus -s migration_temp/migration@xe @"D:\housing\Bat_Files\precreate_tables.sql" > "D:\housing\precreate.log"

echo 3. Running Oracle Import...
imp migration_temp/migration@xe file="D:\housing\DMP\oct_29_06_26.DMP" full=y ignore=y > "D:\housing\imp_output.txt" 2>&1

echo Oracle Import done.
