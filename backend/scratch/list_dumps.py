import os, glob
with open(r'D:\housing\backend\scratch\dumps.txt', 'w', encoding='utf-8') as f:
    for file in glob.glob(r'D:\housing\**\*.dmp', recursive=True):
        f.write(file + '\n')
