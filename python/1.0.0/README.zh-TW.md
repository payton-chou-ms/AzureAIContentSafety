# Azure AI Content Safety 範例程式碼

這個專案包含 Azure AI Content Safety 服務的範例程式碼,支援多種程式語言包括 Python、.NET、Java 和 JavaScript/TypeScript。

## 目錄

- [功能概述](#功能概述)
- [環境設定](#環境設定)
- [Python 範例](#python-範例)
- [.NET 範例](#net-範例)
- [Java 範例](#java-範例)
- [JavaScript/TypeScript 範例](#javascripttypescript-範例)
- [支援與貢獻](#支援與貢獻)

## 功能概述

Azure AI Content Safety 提供以下功能:

- **文字分析**: 偵測文字中的仇恨言論、自我傷害、性內容和暴力內容
- **圖片分析**: 偵測圖片中的不當內容
- **影片分析**: 逐幀分析影片內容
- **封鎖清單管理**: 建立和管理自訂的內容封鎖清單
- **提示盾牌**: 偵測和防護 AI 模型的提示注入攻擊
- **基礎性檢測**: 評估 AI 生成內容的基礎性

## 環境設定

### 前置需求

在開始之前,您需要:

1. Azure 訂閱帳戶
2. Azure AI Content Safety 資源
3. API 金鑰和端點

### 設定環境變數

1. 複製 `.env.template` 檔案並重新命名為 `.env`:
   ```bash
   cp .env.template .env
   ```

2. 編輯 `.env` 檔案,填入您的 Azure AI Content Safety 憑證:
   ```
   CONTENT_SAFETY_ENDPOINT=https://foundry4i2v.cognitiveservices.azure.com/
   CONTENT_SAFETY_KEY=your_actual_api_key_here
   ```

⚠️ **重要**: 請勿將 `.env` 檔案提交到版本控制系統中。此檔案包含敏感資訊。

## Python 範例

### 安裝相依套件

```bash
pip install azure-ai-contentsafety azure-core python-dotenv
```

對於影片分析範例,還需要:
```bash
pip install decord pillow tqdm numpy
```

### 可用範例

#### 1.0.0 版本

位於 `python/1.0.0/` 目錄:

- **`sample_analyze_text.py`**: 同步文字分析
- **`sample_analyze_text_async.py`**: 非同步文字分析
- **`sample_analyze_image.py`**: 同步圖片分析
- **`sample_analyze_image_async.py`**: 非同步圖片分析
- **`sample_analyze_video.py`**: 同步影片分析
- **`sample_analyze_video_async.py`**: 非同步影片分析
- **`sample_analyze_text_with_blocklist.py`**: 使用封鎖清單分析文字
- **`sample_manage_blocklist.py`**: 完整的封鎖清單管理
- **`sample_other_blocklist_operations.py`**: 其他封鎖清單操作
- **`aif_sample_prompt_shields.py`**: 提示盾牌範例
- **`aif_sample_moderate_text_content.py`**: 文字內容審核
- **`aif_sample_groundness_detection.py`**: 基礎性檢測

### 執行範例

```bash
cd python/1.0.0
python sample_analyze_text.py
```

### 範例說明

#### 文字分析

分析文字內容的潛在風險:

```python
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential
import os

client = ContentSafetyClient(
    os.environ["CONTENT_SAFETY_ENDPOINT"],
    AzureKeyCredential(os.environ["CONTENT_SAFETY_KEY"])
)

request = AnalyzeTextOptions(text="您要分析的文字")
response = client.analyze_text(request)
```

#### 圖片分析

分析圖片內容的潛在風險:

```python
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData

with open("image.jpg", "rb") as file:
    request = AnalyzeImageOptions(image=ImageData(content=file.read()))
    response = client.analyze_image(request)
```

#### 封鎖清單管理

建立自訂封鎖清單:

```python
from azure.ai.contentsafety import BlocklistClient
from azure.ai.contentsafety.models import TextBlocklist

blocklist_client = BlocklistClient(
    os.environ["CONTENT_SAFETY_ENDPOINT"],
    AzureKeyCredential(os.environ["CONTENT_SAFETY_KEY"])
)

blocklist = blocklist_client.create_or_update_text_blocklist(
    blocklist_name="MyBlocklist",
    options=TextBlocklist(
        blocklist_name="MyBlocklist",
        description="我的自訂封鎖清單"
    )
)
```

## .NET 範例

### 安裝 NuGet 套件

```bash
dotnet add package Azure.AI.ContentSafety
```

### 可用範例

位於 `dotnet/1.0.0/` 目錄:

- **`AnalyzeText/`**: 文字分析範例
- **`AnalyzeImage/`**: 圖片分析範例
- **`ManageBlocklist/`**: 封鎖清單管理範例

### 執行範例

```bash
cd dotnet/1.0.0/AnalyzeText
dotnet run
```

## Java 範例

### Maven 設定

範例使用 Maven 管理相依性。查看 `pom.xml` 以了解所需的套件。

### 可用範例

位於 `java/1.0.0/src/samples/` 目錄

### 執行範例

```bash
cd java/1.0.0
mvn compile exec:java -Dexec.mainClass="samples.YourSampleClass"
```

## JavaScript/TypeScript 範例

### 安裝 npm 套件

```bash
npm install @azure/ai-content-safety
```

### 可用範例

位於 `js/1.0.0/javascript/` 和 `js/1.0.0/typescript/` 目錄

### 執行 JavaScript 範例

```bash
cd js/1.0.0/javascript
node sample_analyze_text.js
```

### 執行 TypeScript 範例

```bash
cd js/1.0.0/typescript
npm install
npm run build
node dist/sample_analyze_text.js
```

## 內容類別

分析結果會針對以下類別提供嚴重程度評分 (0-7):

- **Hate (仇恨言論)**: 基於種族、民族、性別等的歧視性內容
- **Self-Harm (自我傷害)**: 與自殺或自殘相關的內容
- **Sexual (性內容)**: 性相關的明確內容
- **Violence (暴力)**: 描述暴力行為的內容

嚴重程度級別:
- **0**: 安全
- **2**: 低風險
- **4**: 中等風險
- **6**: 高風險

## 封鎖清單功能

封鎖清單允許您:

1. 建立自訂的文字封鎖清單
2. 新增、更新或刪除封鎖項目
3. 在分析時使用封鎖清單
4. 管理多個封鎖清單

**注意**: 編輯封鎖清單後,通常需要等待 5 分鐘才會生效。

## 最佳實踐

1. **保護您的 API 金鑰**: 永遠不要在程式碼中硬編碼憑證
2. **使用環境變數**: 利用 `.env` 檔案管理設定
3. **錯誤處理**: 實作適當的錯誤處理機制
4. **速率限制**: 注意 API 的速率限制
5. **非同步處理**: 對於大量請求,使用非同步方法
6. **批次處理**: 處理多個項目時考慮批次處理

## 影片分析注意事項

影片分析功能會:
1. 從影片中提取關鍵幀
2. 逐幀分析每個關鍵幀
3. 提供每個時間點的分析結果

預設採樣率為每秒 1 幀,您可以根據需求調整。

## 故障排除

### 常見錯誤

1. **認證錯誤**: 確認 API 金鑰和端點正確
2. **檔案路徑錯誤**: 使用絕對路徑或正確的相對路徑
3. **模組找不到**: 確認已安裝所有必要的套件

### 取得協助

如果遇到問題:
1. 檢查 Azure 入口網站中的資源狀態
2. 驗證環境變數設定正確
3. 查看範例程式碼的錯誤訊息
4. 參考官方文件

## 版本資訊

此專案包含多個 SDK 版本的範例:

- **1.0.0**: 最新穩定版本
- **1.0.0-beta.1**: Beta 測試版本

建議使用 `1.0.0` 版本的範例進行生產環境開發。

## 相關資源

- [Azure AI Content Safety 文件](https://learn.microsoft.com/azure/ai-services/content-safety/)
- [Python SDK 參考](https://learn.microsoft.com/python/api/overview/azure/ai-contentsafety-readme)
- [REST API 參考](https://learn.microsoft.com/rest/api/contentsafety/)
- [定價資訊](https://azure.microsoft.com/pricing/details/cognitive-services/content-safety/)

## 支援與貢獻

### 回報問題

如果您發現錯誤或有功能請求,請在 GitHub 上提出 issue。

### 貢獻指南

歡迎貢獻!請參閱 `CONTRIBUTING.md` 瞭解詳細資訊。

## 授權

此專案採用 MIT 授權。詳見 `LICENSE.md` 檔案。

## 變更日誌

查看 `CHANGELOG.md` 以了解版本變更記錄。

---

**免責聲明**: 這些範例僅供學習和測試用途。在生產環境中使用前,請確保遵循安全最佳實踐和您組織的政策。
