# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
測試 genai_.json - Prompt Shields 檢測
此腳本用於測試 Jailbreak 和 Indirect Attack 攻擊的偵測能力
使用 Azure Content Safety Prompt Shields API 進行真實的攻擊偵測
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List

# 設定輸出編碼為 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_test_data(file_path: str) -> List[Dict]:
    """載入測試資料"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_prompt_shield(endpoint: str, subscription_key: str, prompt: str, system_prompt: str = None) -> Dict:
    """
    使用 Prompt Shields API 偵測 Jailbreak 和 Indirect Attack
    
    Args:
        endpoint: API 端點
        subscription_key: API 金鑰
        prompt: 使用者提示
        system_prompt: 系統提示 (可選,作為 documents)
    
    Returns:
        分析結果字典
    """
    # 建立 API URL (使用 Prompt Shields API)
    api_version = "2024-09-01"
    url = f"{endpoint}/contentsafety/text:shieldPrompt?api-version={api_version}"
    
    # 建立請求標頭
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    
    # 建立請求 body
    # Prompt Shields API 格式: userPrompt + documents
    documents = []
    if system_prompt:
        documents.append(system_prompt)
    
    body = {
        "userPrompt": prompt,
        "documents": documents
    }
    
    try:
        # 發送 API 請求
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        # 解析結果
        result = {
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "system_prompt": system_prompt[:50] + "..." if system_prompt and len(system_prompt) > 50 else system_prompt,
            "attack_detected": False,
            "user_prompt_analysis": {},
            "documents_analysis": []
        }
        
        if response.status_code == 200:
            data = response.json()
            
            # 檢查 userPromptAnalysis
            if "userPromptAnalysis" in data:
                user_analysis = data["userPromptAnalysis"]
                result["user_prompt_analysis"] = user_analysis
                
                # 檢查是否偵測到攻擊
                if user_analysis.get("attackDetected", False):
                    result["attack_detected"] = True
            
            # 檢查 documentsAnalysis
            if "documentsAnalysis" in data:
                result["documents_analysis"] = data["documentsAnalysis"]
                
                # 檢查任何 document 是否偵測到攻擊
                for doc_analysis in data["documentsAnalysis"]:
                    if doc_analysis.get("attackDetected", False):
                        result["attack_detected"] = True
            
            return result
        else:
            # 處理錯誤
            error_data = response.json() if response.text else {}
            return {
                "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "error": True,
                "error_code": error_data.get("error", {}).get("code", response.status_code),
                "error_message": error_data.get("error", {}).get("message", response.text)
            }
            
    except Exception as e:
        return {
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "error": True,
            "error_code": "Exception",
            "error_message": str(e)
        }


def test_genai_dataset(endpoint: str, subscription_key: str, data: List[Dict]) -> Dict:
    """
    測試 genai_.json 資料集 - 使用 Prompt Shields API
    
    Args:
        endpoint: API 端點
        subscription_key: API 金鑰
        data: 測試資料列表
    
    Returns:
        測試結果統計
    """
    print("=" * 80)
    print("開始測試 genai_.json - Prompt Shields 攻擊偵測 (Jailbreak & Indirect Attack)")
    print("=" * 80)
    
    results = {
        "total": len(data),
        "attack_detected": 0,
        "no_attack": 0,
        "errors": 0,
        "details": []
    }
    
    for idx, item in enumerate(data, 1):
        print(f"\n[測試 {idx}/{len(data)}]")
        
        human_prompt = item.get("Human Prompt", "")
        system_prompt = item.get("System Prompt")
        
        # 顯示測試的提示
        print(f"Human Prompt: {human_prompt[:100]}...")
        if system_prompt:
            print(f"System Prompt: {system_prompt[:80]}...")
        
        # 使用 Prompt Shields API 分析
        result = analyze_prompt_shield(endpoint, subscription_key, human_prompt, system_prompt)
        
        # 顯示結果
        if result.get("error"):
            print(f"❌ 錯誤: {result.get('error_message')}")
            results["errors"] += 1
        elif result.get("attack_detected"):
            print(f"✅ 偵測到攻擊!")
            
            # 顯示 User Prompt 分析結果
            user_analysis = result.get("user_prompt_analysis", {})
            if user_analysis:
                print(f"   User Prompt 攻擊偵測: {user_analysis.get('attackDetected', False)}")
            
            # 顯示 Documents 分析結果
            docs_analysis = result.get("documents_analysis", [])
            if docs_analysis:
                for i, doc in enumerate(docs_analysis):
                    print(f"   Document {i+1} 攻擊偵測: {doc.get('attackDetected', False)}")
            
            results["attack_detected"] += 1
        else:
            print(f"⚠️  未偵測到攻擊")
            results["no_attack"] += 1
        
        results["details"].append(result)
        
        # 避免超過 API 速率限制
        time.sleep(1)
    
    return results


def print_summary(results: Dict):
    """列印測試摘要"""
    print("\n" + "=" * 80)
    print("測試摘要")
    print("=" * 80)
    print(f"總測試數: {results['total']}")
    print(f"偵測到攻擊: {results['attack_detected']} ({results['attack_detected']/results['total']*100:.1f}%)")
    print(f"未偵測到: {results['no_attack']} ({results['no_attack']/results['total']*100:.1f}%)")
    print(f"錯誤數: {results['errors']}")
    
    # 統計攻擊偵測率
    print("\n攻擊偵測統計:")
    print("-" * 80)
    
    user_prompt_attacks = 0
    document_attacks = 0
    
    for detail in results['details']:
        if not detail.get('error'):
            # 統計 User Prompt 攻擊
            user_analysis = detail.get('user_prompt_analysis', {})
            if user_analysis.get('attackDetected', False):
                user_prompt_attacks += 1
            
            # 統計 Documents 攻擊
            docs_analysis = detail.get('documents_analysis', [])
            for doc in docs_analysis:
                if doc.get('attackDetected', False):
                    document_attacks += 1
    
    print(f"User Prompt 偵測到攻擊: {user_prompt_attacks}")
    print(f"Documents 偵測到攻擊: {document_attacks}")
    
    print("=" * 80)


def save_results(results: Dict, output_file: str):
    """儲存結果到 JSON 檔案"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n結果已儲存至: {output_file}")


def main():
    # 載入環境變數
    subscription_key = os.environ.get("CONTENT_SAFETY_KEY")
    endpoint = os.environ.get("CONTENT_SAFETY_ENDPOINT")
    
    if not subscription_key or not endpoint:
        print("錯誤: 請設定 CONTENT_SAFETY_KEY 和 CONTENT_SAFETY_ENDPOINT 環境變數")
        print("請確認 .env 檔案已正確設定")
        return
    
    print(f"使用端點: {endpoint}")
    
    # 載入測試資料
    data_file = os.path.join(
        os.path.dirname(__file__), 
        "sample_data_ase", 
        "genai_.json"
    )
    
    if not os.path.exists(data_file):
        print(f"錯誤: 找不到測試資料檔案: {data_file}")
        return
    
    print(f"載入測試資料: {data_file}")
    data = load_test_data(data_file)
    print(f"載入 {len(data)} 筆測試資料\n")
    
    # 執行測試
    results = test_genai_dataset(endpoint, subscription_key, data)
    
    # 列印摘要
    print_summary(results)
    
    # 儲存結果
    output_file = os.path.join(
        os.path.dirname(__file__), 
        "sample_data_ase", 
        "genai_test_results.json"
    )
    save_results(results, output_file)


if __name__ == "__main__":
    main()
