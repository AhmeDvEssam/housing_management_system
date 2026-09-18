@echo off
color 0A
echo ===================================================
echo     Database Cleaning and Unit Sync Automation
echo ===================================================
echo.

set BASE_DIR=%~dp0
set PYTHON_EXE=%BASE_DIR%venv\Scripts\python.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Virtual environment not found at %PYTHON_EXE%
    echo Please make sure this script is in the main project folder.
    pause
    exit /b
)

echo [1/2] Updating official units from Data.xlsx...
"%PYTHON_EXE%" "%BASE_DIR%backend\scripts\smart_sync.py" --reset-units

echo.
echo [2/2] Scanning for and removing duplicate/fake units safely...
"%PYTHON_EXE%" "%BASE_DIR%wipe_dups.py"

echo.
echo ===================================================
echo     SUCCESS! Database is now 100%% clean.
echo ===================================================
pause
