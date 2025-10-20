# 快速測試指南

## 📦 環境設定

### 1. 建立虛擬環境

```bash
# 建立虛擬環境
python3 -m venv .venv

# 啟動虛擬環境
# Linux/macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### 2. 安裝相依套件

```bash
# 安裝 requirements.txt
pip install -r requirements.txt
```

## 🚀 立即執行測試

### Linux/macOS (Bash)

```bash
# 進入目錄
cd AzureAIContentSafety/python/1.0.0/lab

# 測試 1: Prompt Shields (genai_example.json)
dotenv -f ../../../.env run python3 test_genai_prompts.py

# 測試 2: 綜合安全測試 (test_example.json)
dotenv -f ../../../.env run python3 test_comprehensive_safety.py

# 測試 3: Prompt Shields V2 - 綜合分析 (genai_example.json)
dotenv -f ../../../.env run python3 test_genai_prompts_v2.py

# 測試 4: 綜合安全測試 V2 - 綜合分析 (test_example.json)
dotenv -f ../../../.env run python3 test_comprehensive_safety_v2.py
```

### Windows (PowerShell)

```powershell
# 進入目錄
cd AzureAIContentSafety\python\1.0.0\lab

# 測試 1: Prompt Shields (genai_example.json)
dotenv -f ../../../.env run python test_genai_prompts.py

# 測試 2: 綜合安全測試 (test_example.json)
dotenv -f ../../../.env run python test_comprehensive_safety.py

# 測試 3: Prompt Shields V2 - 綜合分析 (genai_example.json)
dotenv -f ../../../.env run python test_genai_prompts_v2.py

# 測試 4: 綜合安全測試 V2 - 綜合分析 (test_example.json)
dotenv -f ../../../.env run python test_comprehensive_safety_v2.py
```

## 📊 輸出檔案

測試完成後會在 `src_data/` 目錄下生成:

### V1 版本 (僅 Prompt Shields API)
- `genai_test_results.json` - genai_example.json 測試結果
- `test_example_results.json` - test_example.json 測試結果

### V2 版本 (綜合分析: Prompt Shields + Content Analysis + Blocklist)
- `genai_test_results_v2.json` - genai_example.json 測試結果 (V2)
- `test_example_results_v2.json` - test_example.json 測試結果 (V2)

## 🔍 查看結果

```bash
# 查看 genai_example 測試結果
cat src_data/genai_test_results.json

# 查看 test_example 測試結果
cat src_data/test_example_results.json
```

## 📈 預期結果

### test_genai_prompts.py (V1)
- 總測試數: 25 筆
- 預期偵測率: > 70%
- 測試時間: 約 30-40 秒
- 使用: Prompt Shields API

### test_comprehensive_safety.py (V1)
- 總測試數: 20 筆
- 預期偵測率: 15-30%
- 測試時間: 約 25-30 秒
- 使用: Prompt Shields API

### test_genai_prompts_v2.py (V2) ⭐ 推薦
- 總測試數: 25 筆
- 預期偵測率: > 95%
- 測試時間: 約 60-80 秒
- 使用: Prompt Shields + Content Analysis + Custom Blocklist

### test_comprehensive_safety_v2.py (V2) ⭐ 推薦
- 總測試數: 20 筆
- 預期偵測率: > 80%
- 測試時間: 約 50-60 秒
- 使用: Prompt Shields + Content Analysis + Custom Blocklist
