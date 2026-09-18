import os
file_path = r'D:\housing\gen_precreate.py'
with open(file_path, 'r', encoding='utf-8') as f:
    data = f.read()

data = data.replace('ddl = \'CREATE TABLE "MIGRATION_TEMP"."{}"\'.format(table_name) + m.group(1).replace(\'\\nREM \', \'\\n\') + \';\'',
                    'ddl = \'DROP TABLE "MIGRATION_TEMP"."{}" CASCADE CONSTRAINTS;\\nCREATE TABLE "MIGRATION_TEMP"."{}"\'.format(table_name, table_name) + m.group(1).replace(\'\\nREM \', \'\\n\') + \';\'')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(data)
