# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
設定 Azure Content Safety Blocklist
此腳本用於建立和管理測試用的 Blocklist
"""

import os
import json
from azure.ai.contentsafety import BlocklistClient
from azure.ai.contentsafety.models import TextBlocklist, AddOrUpdateTextBlocklistItemsOptions, TextBlocklistItem
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError


def create_comprehensive_blocklist():
    """建立綜合安全測試用的 Blocklist (從 custom_blocklist.json 讀取配置)"""
    
    key = os.environ.get("CONTENT_SAFETY_KEY")
    endpoint = os.environ.get("CONTENT_SAFETY_ENDPOINT")
    
    if not key or not endpoint:
        print("錯誤: 請設定 CONTENT_SAFETY_KEY 和 CONTENT_SAFETY_ENDPOINT 環境變數")
        return
    
    # 載入 custom_blocklist.json 配置
    config_file = os.path.join(
        os.path.dirname(__file__),
        "src_data",
        "custom_blocklist.json"
    )
    
    if not os.path.exists(config_file):
        print(f"錯誤: 找不到配置檔案: {config_file}")
        return
    
    print(f"📄 載入配置檔案: {config_file}")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 建立 Blocklist 客戶端
    client = BlocklistClient(endpoint, AzureKeyCredential(key))
    
    blocklist_name = "ComprehensiveSecurityBlocklist"
    blocklist_description = config.get("description", "綜合安全測試用的封鎖清單")
    
    print(f"建立/更新 Blocklist: {blocklist_name}")
    print("=" * 80)
    
    # 1. 建立或更新 Blocklist
    try:
        blocklist = client.create_or_update_text_blocklist(
            blocklist_name=blocklist_name,
            options=TextBlocklist(blocklist_name=blocklist_name, description=blocklist_description),
        )
        if blocklist:
            print(f"✅ Blocklist 已建立/更新: {blocklist.blocklist_name}")
            print(f"   描述: {blocklist.description}\n")
    except HttpResponseError as e:
        print(f"❌ 建立 Blocklist 失敗:")
        if e.error:
            print(f"   Error code: {e.error.code}")
            print(f"   Error message: {e.error.message}")
        return
    
    # 2. 從配置檔案讀取關鍵字
    categories = config.get("categories", {})
    
    if not categories:
        print("錯誤: 配置檔案中沒有定義任何類別")
        return
    
    print(f"📋 已載入 {len(categories)} 個類別")
    
    # 組織 blocklist 項目資料
    blocklist_items_data = {}
    for category_key, category_data in categories.items():
        category_name = category_data.get("description", category_key)
        keywords = category_data.get("keywords", [])
        
        if keywords:
            blocklist_items_data[category_name] = keywords
            print(f"   - {category_name}: {len(keywords)} 個關鍵字")
    
    # 3. 加入所有關鍵字到 Blocklist
    print("加入封鎖關鍵字...")
    print("-" * 80)
    
    total_items = 0
    for category, keywords in blocklist_items_data.items():
        print(f"\n📋 類別: {category}")
        
        # 每次最多加入 100 個項目 (API 限制)
        batch_size = 100
        for i in range(0, len(keywords), batch_size):
            batch_keywords = keywords[i:i+batch_size]
            
            blocklist_items = [
                TextBlocklistItem(text=keyword, description=f"{category} - {keyword}")
                for keyword in batch_keywords
            ]
            
            try:
                result = client.add_or_update_blocklist_items(
                    blocklist_name=blocklist_name,
                    options=AddOrUpdateTextBlocklistItemsOptions(blocklist_items=blocklist_items)
                )
                
                if result and result.blocklist_items:
                    for item in result.blocklist_items:
                        print(f"   ✅ {item.text}")
                        total_items += 1
                        
            except HttpResponseError as e:
                print(f"   ❌ 加入關鍵字失敗:")
                if e.error:
                    print(f"      Error code: {e.error.code}")
                    print(f"      Error message: {e.error.message}")
    
    print("\n" + "=" * 80)
    print(f"✅ 完成! 共加入 {total_items} 個封鎖項目")
    print(f"📝 Blocklist 名稱: {blocklist_name}")
    print("\n⚠️  注意: Blocklist 通常需要 5 分鐘才會生效,請稍後再執行測試。")
    print("=" * 80)


def list_current_blocklists():
    """列出目前所有的 Blocklists"""
    
    key = os.environ.get("CONTENT_SAFETY_KEY")
    endpoint = os.environ.get("CONTENT_SAFETY_ENDPOINT")
    
    if not key or not endpoint:
        print("錯誤: 請設定 CONTENT_SAFETY_KEY 和 CONTENT_SAFETY_ENDPOINT 環境變數")
        return
    
    client = BlocklistClient(endpoint, AzureKeyCredential(key))
    
    print("\n目前的 Blocklists:")
    print("=" * 80)
    
    try:
        blocklists = client.list_text_blocklists()
        if blocklists:
            for blocklist in blocklists:
                print(f"📋 名稱: {blocklist.blocklist_name}")
                print(f"   描述: {blocklist.description}")
                
                # 列出此 blocklist 的項目
                try:
                    items = client.list_text_blocklist_items(blocklist_name=blocklist.blocklist_name)
                    item_count = len(list(items))
                    print(f"   項目數: {item_count}")
                except:
                    print(f"   項目數: 無法取得")
                print()
        else:
            print("目前沒有任何 Blocklist")
    except HttpResponseError as e:
        print(f"❌ 列出 Blocklists 失敗:")
        if e.error:
            print(f"   Error code: {e.error.code}")
            print(f"   Error message: {e.error.message}")
    
    print("=" * 80)


def delete_blocklist(blocklist_name: str):
    """刪除指定的 Blocklist"""
    
    key = os.environ.get("CONTENT_SAFETY_KEY")
    endpoint = os.environ.get("CONTENT_SAFETY_ENDPOINT")
    
    if not key or not endpoint:
        print("錯誤: 請設定 CONTENT_SAFETY_KEY 和 CONTENT_SAFETY_ENDPOINT 環境變數")
        return
    
    client = BlocklistClient(endpoint, AzureKeyCredential(key))
    
    try:
        client.delete_text_blocklist(blocklist_name=blocklist_name)
        print(f"✅ 已刪除 Blocklist: {blocklist_name}")
    except HttpResponseError as e:
        print(f"❌ 刪除 Blocklist 失敗:")
        if e.error:
            print(f"   Error code: {e.error.code}")
            print(f"   Error message: {e.error.message}")


def main():
    print("Azure Content Safety Blocklist 設定工具")
    print("=" * 80)
    print("\n選項:")
    print("1. 建立/更新綜合安全測試 Blocklist")
    print("2. 列出所有 Blocklists")
    print("3. 刪除 Blocklist")
    print("0. 全部執行 (建立並列出)")
    print()
    
    choice = input("請選擇操作 (0-3): ").strip()
    
    if choice == "1":
        create_comprehensive_blocklist()
    elif choice == "2":
        list_current_blocklists()
    elif choice == "3":
        blocklist_name = input("請輸入要刪除的 Blocklist 名稱: ").strip()
        if blocklist_name:
            confirm = input(f"確定要刪除 '{blocklist_name}'? (yes/no): ").strip().lower()
            if confirm == "yes":
                delete_blocklist(blocklist_name)
    elif choice == "0":
        create_comprehensive_blocklist()
        print("\n")
        list_current_blocklists()
    else:
        print("無效的選擇")


if __name__ == "__main__":
    main()
