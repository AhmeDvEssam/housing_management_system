import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
df = pd.read_excel(r'D:\housing\Data.xlsx')
print(df.columns.tolist())
print(df.head(2).to_dict('records'))
