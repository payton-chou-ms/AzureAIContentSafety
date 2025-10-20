# Azure Content Safety 測試說明

## 📋 測試檔案說明

### 1. test_genai_prompts.py
- **測試資料**: `genai_example.json`
- **API**: Prompt Shields API (`text:shieldPrompt`)
- **測試項目**: Jailbreak 和 Indirect Attack
- **資料結構**: 
  - `Human Prompt`: 使用者輸入的提示
  - `System Prompt`: 系統提示(僅記錄,不送入 API)
- **預期偵測率**: > 70%

### 2. test_comprehensive_safety.py
- **測試資料**: `test_example.json`
- **API**: Prompt Shields API (`text:shieldPrompt`)
- **測試項目**: 
  - 繞過指令限制
  - 角色扮演攻擊
  - 多層嵌套提示
  - 語言混淆
  - 企業機密
  - 惡意連結偵測
- **資料結構**: 
  - `prompt`: 測試提示
  - `測試目的`: 測試目標
  - `測試項目`: 測試類別
- **預期偵測率**: 15-30%

## ⚠️ 重要說明

### Prompt Shields API 的偵測範圍

Prompt Shields API 主要針對以下兩種攻擊類型:

1. **Jailbreak 攻擊**: 試圖繞過 AI 系統的安全限制
2. **Indirect Attack**: 間接攻擊,通過文檔注入等方式

### 不在 Prompt Shields 偵測範圍內的項目

以下測試項目**不會**被 Prompt Shields API 偵測為攻擊:

- ❌ **惡意連結**: Prompt Shields 不進行 URL 分析
- ❌ **企業機密資料**: 需要使用自定義規則或其他 API
- ❌ **語言混淆**: 部分混淆手法可能無法被偵測
- ❌ **多層嵌套提示**: 取決於嵌套的複雜度

### 預期偵測項目

以下測試項目**有機會**被 Prompt Shields 偵測:

- ✅ **繞過指令限制**: 特別是明確要求忽略先前指示的提示
- ✅ **角色扮演攻擊**: 要求 AI 扮演特定角色以繞過限制
- ⚠️ **多層嵌套提示**: 視複雜度而定

## 📊 測試結果解讀

### genai_example.json
這個資料集主要針對 Jailbreak 攻擊,預期有高偵測率(70%+)。

### test_example.json
這個資料集包含多種測試類型,但只有部分項目在 Prompt Shields 的偵測範圍內:

| 測試項目 | 預期偵測率 | 說明 |
|---------|----------|------|
| 繞過指令限制 | 30-50% | 部分會被偵測 |
| 角色扮演攻擊 | 60-80% | 高機率被偵測 |
| 多層嵌套提示 | 0-20% | 較難偵測 |
| 語言混淆 | 0-10% | 基本不會偵測 |
| 企業機密 | 0% | 不在偵測範圍 |
| 釣魚/惡意連結 | 0% | 不在偵測範圍 |

**整體預期偵測率**: 15-30%

## 🔧 使用說明

### 執行測試

```bash
# 進入測試目錄
cd AzureAIContentSafety/python/1.0.0/lab

# 測試 1: genai_example.json
dotenv -f ../../../.env run python test_genai_prompts.py

# 測試 2: test_example.json
dotenv -f ../../../.env run python test_comprehensive_safety.py
```

### 查看結果

```bash
# 查看 genai_example 測試結果
cat src_data/genai_test_results.json

# 查看 test_example 測試結果
cat src_data/test_example_results.json
```

## 💡 建議

如果需要偵測以下項目,建議使用其他 Azure Content Safety API:

1. **惡意連結偵測**: 需要額外的 URL 分析服務
2. **敏感資料識別**: 使用 Azure AI Content Safety 的文字分析 API
3. **自定義關鍵字**: 使用 Blocklist 功能
4. **內容分類**: 使用 `text:analyze` API 進行內容安全分析

## 📝 輸出格式

所有測試結果會包含完整的 prompt 內容,並儲存在對應的 JSON 檔案中:

- `genai_test_results.json`: genai_example.json 的測試結果
- `test_example_results.json`: test_example.json 的測試結果

每筆結果包含:
- `prompt`: 完整的測試提示
- `system_prompt`: 系統提示(如果有,僅 genai_example.json)
- `attack_detected`: 是否偵測到攻擊
- `user_prompt_analysis`: 使用者提示分析結果
- `documents_analysis`: 文檔分析結果(通常為空,因為不送入 documents)
