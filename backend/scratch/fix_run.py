import os

f3 = r'D:\housing\Bat_Files\3_Run_Server.bat'
with open(f3, 'r', encoding='utf-8') as f:
    content3 = f.read()

# Fix Postgres service dynamically
old_pg = 'net start postgresql-x64-18 >nul 2>&1'
new_pg = '''for /f "tokens=2" %%S in ('sc query state^= all ^| findstr /I "SERVICE_NAME: postgresql"') do (
    net start "%%S" >nul 2>&1
)'''
content3 = content3.replace(old_pg, new_pg)

# Fix Port 80
if 'netstat -ano | find' not in content3:
    port_logic = '''echo Checking Port Availability...
netstat -ano | find ":80 " >nul 2>&1
if %errorLevel% equ 0 (
    echo [WARNING] Port 80 is occupied (Maybe IIS or Skype). Switching to Port 8000!
    set PORT=8000
) else (
    set PORT=80
)

echo Starting Housing Project Server...'''
    content3 = content3.replace('echo Starting Housing Project Server...', port_logic)
    
    # replace hardcoded 80s
    content3 = content3.replace('Port 80\n', 'Port %PORT%\n')
    content3 = content3.replace('--listen=0.0.0.0:80 ', '--listen=0.0.0.0:%PORT% ')
    content3 = content3.replace('http://localhost/dashboard/', 'http://localhost:%PORT%/dashboard/')
    content3 = content3.replace('http://localhost/admin/', 'http://localhost:%PORT%/admin/')

with open(f3, 'w', encoding='utf-8') as f:
    f.write(content3)
print('Updated 3_Run_Server.bat')
