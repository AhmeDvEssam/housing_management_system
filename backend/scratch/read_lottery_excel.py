import pandas as pd
import json
import sys
import io

try:
    df = pd.read_excel(r'd:\housing\تحليل\نتيجه قرعة 2026.xlsx')
    data = df.head(20).to_dict(orient='records')
    with open(r'd:\housing\backend\scratch\lottery_excel_sample.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
