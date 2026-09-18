import subprocess
p = subprocess.Popen([r'D:\housing\Bat_Files\pg_backup.bat'], cwd=r'D:\housing\Bat_Files', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate(b'\n')
with open(r'D:\housing\backend\scratch\backup_out2.txt', 'wb') as f:
    f.write(out)
    f.write(err)
