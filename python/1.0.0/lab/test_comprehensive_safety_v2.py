# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
測試 test_example.json - 綜合安全測試 V2
此版本結合多種 Azure Content Safety API:
1. Prompt Shields API - Jailbreak/Indirect Attack 偵測
2. Text Analyze API - 內容安全分析 (暴力、仇恨、性、自殘)
3. Azure Blocklist API - 使用 Azure Content Safety Blocklist 進行關鍵字偵測
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# 設定輸出編碼為 UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Azure Blocklist 名稱 (需先執行 setup_blocklist.py 建立)
BLOCKLIST_NAME = "ComprehensiveSecurityBlocklist"


def load_test_data(file_path: str) -> List[Dict]:
    """載入測試資料"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_azure_blocklist(endpoint: str, subscription_key: str, prompt: str) -> Dict:
    """
    使用 Azure Content Safety Blocklist API 檢查提示
    
    Args:
        endpoint: Azure Content Safety endpoint
        subscription_key: API 金鑰
        prompt: 測試提示
    
    Returns:
        偵測結果
    """
    try:
        # 建立 Content Safety 客戶端
        client = ContentSafetyClient(endpoint, AzureKeyCredential(subscription_key))
        
        # 使用 AnalyzeTextOptions 配合 blocklist
        # 注意: Blocklist 通常需要 5 分鐘才會生效
        analysis_result = client.analyze_text(
            AnalyzeTextOptions(
                text=prompt, 
                blocklist_names=[BLOCKLIST_NAME], 
                halt_on_blocklist_hit=False
            )
        )
        
        matches = []
        if analysis_result and analysis_result.blocklists_match:
            for match_result in analysis_result.blocklists_match:
                matches.append({
                    "blocklist_name": match_result.blocklist_name,
                    "blocklist_item_id": match_result.blocklist_item_id,
                    "blocklist_item_text": match_result.blocklist_item_text
                })
        
        return {
            "success": True,
            "blocked": len(matches) > 0,
            "matches": matches,
            "total_matches": len(matches)
        }
        
    except HttpResponseError as e:
        error_msg = f"{e.error.code}: {e.error.message}" if e.error else str(e)
        return {
            "success": False,
            "blocked": False,
            "matches": [],
            "total_matches": 0,
            "error": error_msg
        }
    except Exception as e:
        return {
            "success": False,
            "blocked": False,
            "matches": [],
            "total_matches": 0,
            "error": str(e)
        }


def analyze_prompt_shield(endpoint: str, subscription_key: str, prompt: str) -> Dict:
    """
    使用 Prompt Shields API 偵測 Jailbreak 和 Indirect Attack
    """
    api_version = "2024-09-01"
    url = f"{endpoint}/contentsafety/text:shieldPrompt?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    
    body = {
        "userPrompt": prompt,
        "documents": []
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            user_analysis = data.get("userPromptAnalysis", {})
            
            return {
                "success": True,
                "attack_detected": user_analysis.get("attackDetected", False),
                "analysis": user_analysis
            }
        else:
            error_data = response.json() if response.text else {}
            return {
                "success": False,
                "error": error_data.get("error", {}).get("message", response.text)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def analyze_text_content(endpoint: str, subscription_key: str, prompt: str) -> Dict:
    """
    使用 Text Analyze API 分析內容安全性
    """
    api_version = "2024-09-01"
    url = f"{endpoint}/contentsafety/text:analyze?api-version={api_version}"
    
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": subscription_key
    }
    
    body = {
        "text": prompt
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            categories_analysis = data.get("categoriesAnalysis", [])
            
            # 檢查是否有任何類別的嚴重程度 >= 2
            threat_detected = False
            high_risk_categories = {}
            
            for category in categories_analysis:
                cat_name = category.get("category", "Unknown")
                severity = category.get("severity", 0)
                
                if severity >= 2:
                    threat_detected = True
                    high_risk_categories[cat_name] = severity
            
            return {
                "success": True,
                "threat_detected": threat_detected,
                "high_risk_categories": high_risk_categories,
                "all_categories": {cat.get("category"): cat.get("severity") for cat in categories_analysis}
            }
        else:
            error_data = response.json() if response.text else {}
            return {
                "success": False,
                "error": error_data.get("error", {}).get("message", response.text)
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def comprehensive_analysis(
    endpoint: str,
    subscription_key: str,
    prompt: str,
    test_purpose: str = None,
    test_category: str = None
) -> Dict:
    """
    綜合分析 - 結合多種檢測方法 (使用 Azure Blocklist API)
    """
    result = {
        "prompt": prompt,
        "test_purpose": test_purpose,
        "test_category": test_category,
        "overall_threat_detected": False,
        "detection_methods": {
            "prompt_shield": {},
            "content_analysis": {},
            "azure_blocklist": {}
        }
    }
    
    # 1. Azure Blocklist 檢查
    blocklist_result = check_azure_blocklist(endpoint, subscription_key, prompt)
    result["detection_methods"]["azure_blocklist"] = blocklist_result
    if blocklist_result["blocked"]:
        result["overall_threat_detected"] = True
    
    # 2. Prompt Shields 檢查
    shield_result = analyze_prompt_shield(endpoint, subscription_key, prompt)
    result["detection_methods"]["prompt_shield"] = shield_result
    if shield_result.get("success") and shield_result.get("attack_detected"):
        result["overall_threat_detected"] = True
    
    # 3. Content Analysis 檢查
    content_result = analyze_text_content(endpoint, subscription_key, prompt)
    result["detection_methods"]["content_analysis"] = content_result
    if content_result.get("success") and content_result.get("threat_detected"):
        result["overall_threat_detected"] = True
    
    return result


def test_comprehensive_dataset(
    endpoint: str,
    subscription_key: str,
    data: List[Dict]
) -> Dict:
    """
    測試 test_example.json 資料集 - 使用綜合分析
    """
    print("=" * 80)
    print("開始測試 test_example.json - 綜合安全分析 V2")
    print(f"偵測方法: Prompt Shields + Content Analysis + Azure Blocklist ({BLOCKLIST_NAME})")
    print("=" * 80)
    
    results = {
        "total": len(data),
        "overall_detected": 0,
        "no_threat": 0,
        "detection_breakdown": {
            "prompt_shield": 0,
            "content_analysis": 0,
            "azure_blocklist": 0,
            "multiple_methods": 0
        },
        "by_category": {},
        "details": []
    }
    
    for idx, item in enumerate(data, 1):
        print(f"\n[測試 {idx}/{len(data)}]")
        print("=" * 80)
        
        prompt = item.get("prompt", "")
        test_purpose = item.get("測試目的")
        test_category = item.get("測試項目")
        
        print(f"完整 Prompt:")
        print("-" * 80)
        print(prompt)
        print("-" * 80)
        
        if test_purpose:
            print(f"測試目的: {test_purpose}")
        if test_category:
            print(f"測試項目: {test_category}")
        
        # 綜合分析
        result = comprehensive_analysis(
            endpoint,
            subscription_key,
            prompt,
            test_purpose,
            test_category
        )
        
        # 顯示結果
        if result["overall_threat_detected"]:
            print(f"\n✅ 偵測到威脅!")
            
            # 顯示各檢測方法的結果
            detection_methods = []
            
            if result["detection_methods"]["azure_blocklist"]["blocked"]:
                detection_methods.append("Azure Blocklist")
                print(f"   📋 Azure Blocklist 偵測:")
                print(f"      匹配項目數: {result['detection_methods']['azure_blocklist']['total_matches']}")
                matches = result['detection_methods']['azure_blocklist']['matches']
                for match in matches[:5]:  # 最多顯示 5 個
                    print(f"      - {match['blocklist_item_text']}")
            
            if result["detection_methods"]["prompt_shield"].get("attack_detected"):
                detection_methods.append("Prompt Shield")
                print(f"   🛡️  Prompt Shield 偵測: 攻擊已偵測")
            
            if result["detection_methods"]["content_analysis"].get("threat_detected"):
                detection_methods.append("Content Analysis")
                print(f"   📊 Content Analysis 偵測:")
                high_risk = result["detection_methods"]["content_analysis"]["high_risk_categories"]
                for cat, severity in high_risk.items():
                    print(f"      {cat}: {severity}")
            
            print(f"   偵測方法: {', '.join(detection_methods)}")
            
            # 統計
            if len(detection_methods) > 1:
                results["detection_breakdown"]["multiple_methods"] += 1
            results["overall_detected"] += 1
        else:
            print(f"\n⚠️  未偵測到威脅")
            results["no_threat"] += 1
        
        # 統計各偵測方法
        if result["detection_methods"]["prompt_shield"].get("attack_detected"):
            results["detection_breakdown"]["prompt_shield"] += 1
        if result["detection_methods"]["content_analysis"].get("threat_detected"):
            results["detection_breakdown"]["content_analysis"] += 1
        if result["detection_methods"]["azure_blocklist"]["blocked"]:
            results["detection_breakdown"]["azure_blocklist"] += 1
        
        # 統計各測試項目
        if test_category:
            if test_category not in results["by_category"]:
                results["by_category"][test_category] = {
                    "total": 0,
                    "detected": 0
                }
            results["by_category"][test_category]["total"] += 1
            if result["overall_threat_detected"]:
                results["by_category"][test_category]["detected"] += 1
        
        results["details"].append(result)
        
        # 避免超過 API 速率限制
        time.sleep(1)
    
    return results


def print_summary(results: Dict):
    """列印測試摘要"""
    print("\n" + "=" * 80)
    print("測試摘要 - 綜合安全分析 V2")
    print("=" * 80)
    print(f"總測試數: {results['total']}")
    print(f"偵測到威脅: {results['overall_detected']} ({results['overall_detected']/results['total']*100:.1f}%)")
    print(f"未偵測到: {results['no_threat']} ({results['no_threat']/results['total']*100:.1f}%)")
    
    print("\n偵測方法統計:")
    print("-" * 80)
    print(f"Prompt Shield 偵測: {results['detection_breakdown']['prompt_shield']}")
    print(f"Content Analysis 偵測: {results['detection_breakdown']['content_analysis']}")
    print(f"Azure Blocklist 偵測: {results['detection_breakdown']['azure_blocklist']}")
    print(f"多重方法偵測: {results['detection_breakdown']['multiple_methods']}")
    
    if results["by_category"]:
        print("\n各測試項目偵測率:")
        print("-" * 80)
        for category, stats in results["by_category"].items():
            detection_rate = (stats["detected"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"{category}")
            print(f"  偵測率: {stats['detected']}/{stats['total']} ({detection_rate:.1f}%)")
    
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
    print(f"使用 Azure Blocklist: {BLOCKLIST_NAME}")
    print("⚠️  注意: 請確保已執行 setup_blocklist.py 建立 Blocklist,且已等待 5 分鐘生效\n")
    
    # 載入測試資料
    data_file = os.path.join(
        os.path.dirname(__file__), 
        "src_data", 
        "test_example.json"
    )
    
    if not os.path.exists(data_file):
        print(f"錯誤: 找不到測試資料檔案: {data_file}")
        return
    
    print(f"載入測試資料: {data_file}")
    data = load_test_data(data_file)
    print(f"載入 {len(data)} 筆測試資料\n")
    
    # 執行測試
    results = test_comprehensive_dataset(endpoint, subscription_key, data)
    
    # 列印摘要
    print_summary(results)
    
    # 儲存結果
    output_file = os.path.join(
        os.path.dirname(__file__), 
        "src_data", 
        "test_example_results_v2.json"
    )
    save_results(results, output_file)


if __name__ == "__main__":
    main()
