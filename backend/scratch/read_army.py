import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_csv(r'D:\housing\army_contracts_146.csv')
print(df.head())
print('Total rows:', len(df))
