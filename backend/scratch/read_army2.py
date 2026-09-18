import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')
try:
    df = pd.read_csv(r'D:\housing\army_contracts_new.csv')
    print('army_contracts_new.csv rows:', len(df))
except Exception as e:
    print('Error:', e)
