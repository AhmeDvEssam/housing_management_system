import pandas as pd
import json

try:
    df = pd.read_excel(r'd:\housing\تحليل\نتيجه قرعة 2026.xlsx', sheet_name='Sheet 1')
    data = df.head(50).to_dict(orient='records')
    with open(r'd:\housing\backend\scratch\lottery_excel_sample_s1.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
