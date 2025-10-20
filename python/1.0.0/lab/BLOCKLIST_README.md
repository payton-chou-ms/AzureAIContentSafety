# Azure Content Safety - 使用官方 Blocklist API 的 V2 測試

## 概述

V2 版本整合三種 Azure Content Safety API 來提供多層次的威脅偵測:

1. **Prompt Shields API** - 偵測 Jailbreak 和 Indirect Attack
2. **Text Analyze API** - 分析內容安全 (暴力、仇恨、性、自殘)
3. **Azure Blocklist API** - 使用 Azure Content Safety 官方 Blocklist 進行關鍵字偵測

## 使用步驟

### 步驟 1: 建立 Azure Blocklist

首先需要建立包含關鍵字的 Blocklist:

```bash
cd lab
dotenv -f ../../../.env run py setup_blocklist.py
```

選擇選項 `1` 或 `0` 來建立 Blocklist。

**重要**: Blocklist 建立後需要約 **5 分鐘**才會生效,請等待後再執行測試。

### 步驟 2: 查看 Blocklist 內容

```bash
dotenv -f ../../../.env run py setup_blocklist.py
```

選擇選項 `2` 來查看目前的 Blocklists。

### 步驟 3: 執行測試

等待 5 分鐘後,執行 V2 測試:

```bash
# 測試 test_example.json (綜合安全測試)
dotenv -f ../../../.env run py test_comprehensive_safety_v2.py

# 測試 genai_example.json (GenAI Prompt 測試)
dotenv -f ../../../.env run py test_genai_prompts_v2.py
```

## Blocklist 內容

`setup_blocklist.py` 會建立名為 `ComprehensiveSecurityBlocklist` 的 Blocklist,包含以下類別:

1. **繞過指令限制** - "忽略所有先前的指示", "ignore previous", "bypass security" 等
2. **權限提升** - "最高權限", "elevate privilege", "sudo" 等
3. **資料外洩** - "列出所有資料庫", "dump database", "export data" 等
4. **惡意程式碼** - "builtins.exec", "subprocess.check_output", "os.system" 等
5. **角色扮演攻擊** - "你現在擔任", "假裝你是", "pretend you are" 等
6. **敏感資料** - "員工工號", "合約金額", "薪資明細" 等
7. **惡意連結特徵** - ".ru/", ".shop/api", "execute_dll.exe" 等

## 檔案說明

### setup_blocklist.py

管理 Azure Blocklist 的工具:
- 建立/更新 Blocklist
- 列出所有 Blocklists
- 刪除 Blocklist

### test_comprehensive_safety_v2.py

測試 `test_example.json` 資料集,使用三層偵測:
- 整合 Prompt Shields + Content Analysis + Azure Blocklist
- 輸出詳細的偵測結果和統計資訊
- 預期偵測率: 85%+ (vs V1 的 15-30%)

### test_genai_prompts_v2.py

測試 `genai_example.json` 資料集:
- 整合 Prompt Shields + Content Analysis + Azure Blocklist
- 同時檢查 Human Prompt 和 System Prompt
- 預期偵測率: 95%+ (vs V1 的 70%)

## 與之前版本的差異

### 之前 (自定義 Blocklist)

- 使用本地 `custom_blocklist.json` 檔案
- 簡單的字串匹配
- 需要手動維護關鍵字列表
- 不需要等待時間

### 現在 (Azure Blocklist API)

- 使用 Azure Content Safety 官方 Blocklist API
- 整合到 Azure 平台中
- 統一管理和版本控制
- 需要 5 分鐘生效時間
- 可透過 API 動態更新
- 支援跨專案共享 Blocklist

## 優點

1. **集中管理**: Blocklist 儲存在 Azure 上,可跨多個應用程式共享
2. **動態更新**: 可透過 API 動態新增/移除關鍵字
3. **版本控制**: Azure 會管理 Blocklist 的版本
4. **效能更好**: Azure 的匹配演算法比簡單字串匹配更有效率
5. **官方支援**: 使用 Azure 官方 API,有完整的文件和支援

## 注意事項

1. **等待時間**: Blocklist 建立或更新後需要約 5 分鐘才會生效
2. **API 限制**: 一次最多可加入 100 個項目到 Blocklist
3. **命名規則**: Blocklist 名稱必須唯一
4. **刪除操作**: 刪除 Blocklist 會同時刪除所有項目,無法復原

## 疑難排解

### 錯誤: Blocklist not found

確認已執行 `setup_blocklist.py` 建立 Blocklist。

### 沒有任何匹配

確認已等待 5 分鐘讓 Blocklist 生效。

### API 錯誤

檢查 `.env` 檔案中的 `CONTENT_SAFETY_KEY` 和 `CONTENT_SAFETY_ENDPOINT` 是否正確設定。

## 參考資料

- [Azure Content Safety Blocklist 文件](https://learn.microsoft.com/azure/ai-services/content-safety/how-to/use-blocklist)
- [Prompt Shields API 文件](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-jailbreak)
- [Text Analyze API 文件](https://learn.microsoft.com/azure/ai-services/content-safety/quickstart-text)
