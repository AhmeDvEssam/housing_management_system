import pandas as pd
import json

try:
    xl = pd.ExcelFile(r'd:\housing\تحليل\نتيجه قرعة 2026.xlsx')
    print(json.dumps(xl.sheet_names, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
