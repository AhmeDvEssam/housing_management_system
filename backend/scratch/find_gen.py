import os, glob
with open(r'D:\housing\backend\scratch\find_gen.txt', 'w', encoding='utf-8') as f:
    for file in glob.glob(r'D:\housing\**\gen_precreate*.py', recursive=True):
        f.write(file + '\n')
