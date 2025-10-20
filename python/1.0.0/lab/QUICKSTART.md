# 快速測試指南

## 🚀 立即執行測試

### Windows (PowerShell)

```powershell
# 進入目錄
cd C:\Users\chihengchou\Downloads\work\AzureAIContentSafety\python\1.0.0

# 測試 1: Prompt Shields (genai_.json)
python test_genai_prompts.py

# 測試 2: 綜合安全測試 (test_example.json)
python test_comprehensive_safety.py
```

### Linux/macOS (Bash)

```bash
# 進入目錄
cd /mnt/c/Users/chihengchou/Downloads/work/AzureAIContentSafety/python/1.0.0

# 測試 1: Prompt Shields (genai_.json)
python3 test_genai_prompts.py

# 測試 2: 綜合安全測試 (test_example.json)
python3 test_comprehensive_safety.py
```

## 📊 輸出檔案

測試完成後會在 `sample_data_ase/` 目錄下生成:

- `genai_test_results.json` - genai_.json 測試結果
- `test_example_results.json` - test_example.json 測試結果

## ⚡ 一鍵執行所有測試

### Windows (PowerShell)

```powershell
# 執行所有測試
python test_genai_prompts.py && python test_comprehensive_safety.py
```

### Linux/macOS

```bash
# 執行所有測試
python3 test_genai_prompts.py && python3 test_comprehensive_safety.py
```

## 🔍 查看結果

```bash
# 查看 genai_ 測試結果
cat sample_data_ase/genai_test_results.json

# 查看 test_example 測試結果
cat sample_data_ase/test_example_results.json
```

## 📈 預期結果

### test_genai_prompts.py
- 總測試數: 25 筆
- 預期偵測率: > 70%
- 測試時間: 約 30-40 秒

### test_comprehensive_safety.py
- 總測試數: 20 筆
- 預期偵測率: > 80%
- 測試時間: 約 25-30 秒

## ⚠️ 注意事項

1. **API 速率限制**: 兩個測試之間建議間隔 5-10 秒
2. **網路連線**: 需要穩定的網路連線到 Azure
3. **環境變數**: 確保 `.env` 檔案已正確設定
4. **Python 版本**: 需要 Python 3.8 或更高版本

## 🐛 常見問題

### Q: UnicodeEncodeError
A: 已修正,腳本會自動處理編碼問題

### Q: 找不到測試資料
A: 確認目前目錄在 `python/1.0.0/`

### Q: API Key 錯誤
A: 檢查 `.env` 檔案中的 `CONTENT_SAFETY_KEY`

### Q: 連線逾時
A: 檢查 `CONTENT_SAFETY_ENDPOINT` 是否正確
