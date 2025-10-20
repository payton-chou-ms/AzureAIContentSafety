#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pandas as pd
import os

# 取得當前腳本所在目錄
script_dir = os.path.dirname(os.path.abspath(__file__))

# 讀取 genai_.xlsx
print("正在處理 genai_.xlsx...")
df1 = pd.read_excel(os.path.join(script_dir, 'genai_.xlsx'))
data1 = df1.to_dict(orient='records')

# 將 NaN 轉換為 None (在 JSON 中會變成 null)
for record in data1:
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None

# 儲存為 JSON
with open(os.path.join(script_dir, 'genai_example.json'), 'w', encoding='utf-8') as f:
    json.dump(data1, f, ensure_ascii=False, indent=2)

print(f'✓ genai_example.json 已成功創建 (共 {len(data1)} 筆資料)')

# 讀取 test_example.xlsx
print("\n正在處理 test_example.xlsx...")
df2 = pd.read_excel(os.path.join(script_dir, 'test_example.xlsx'))
data2 = df2.to_dict(orient='records')

# 將 NaN 轉換為 None
for record in data2:
    for key, value in record.items():
        if pd.isna(value):
            record[key] = None

# 儲存為 JSON
with open(os.path.join(script_dir, 'test_example.json'), 'w', encoding='utf-8') as f:
    json.dump(data2, f, ensure_ascii=False, indent=2)

print(f'✓ test_example.json 已成功創建 (共 {len(data2)} 筆資料)')
print("\n所有檔案轉換完成!")
