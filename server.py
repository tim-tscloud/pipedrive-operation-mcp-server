from fastmcp import FastMCP
from typing import Optional, List, Dict, Any

import requests
import asyncio

PIPEDRIVE_TOKEN = "b8928b87616ec392587b44268757fa8b9353a95b"
PIPEDRIVE_BASE = "https://api.pipedrive.com/api/v2"
PIPEDRIVE_DOMAIN = "tscloudwork"

mcp = FastMCP("chatgpt-pd-operation")

# ===== 核心邏輯，負責和 Pipedrive API 溝通，可以在任何地方被呼叫 =====

def _logic_search_pipedrive_person(name: str = None, email: str = None) -> Optional[Dict[str, Any]]: # type: ignore
    """
    搜尋 Pipedrive 中是否存在指定名稱或 email 的聯絡人
    優先使用 email 搜尋（更精確），若無則使用名稱
    返回找到的第一個聯絡人，若無則返回 None
    """
    headers = {
        "x-api-token": PIPEDRIVE_TOKEN,
        "Content-Type": "application/json"
    }

    # 優先使用 email 搜尋
    if email:
        params = {
            "term": email,
            "fields": "email",
            "exact_match": "true",
            "limit": 1
        }
    elif name:
        params = {
            "term": name,
            "fields": "name",
            "exact_match": "true",
            "limit": 1
        }
    else:
        return None
    
    try:
        res = requests.get(
            f"{PIPEDRIVE_BASE}/persons/search",
            params=params,
            headers=headers
        )
        res.raise_for_status()
        data = res.json()

        if data.get("success") and data.get("data") and len(data["data"]["items"]) > 0:
            return data["data"]["items"][0]["item"]
        return None
    
    except Exception as e:
        print(f"搜尋聯絡人時發生錯誤: {e}")
        return None


def _logic_search_pipedrive_organization(name: str, tax_id: str) -> Optional[Dict[str, Any]]:
    """
    搜尋 Pipedrive 中是否存在指定名稱或統一編號的組織
    優先使用統一編號搜尋（更精確），若無則使用名稱
    返回找到的第一個組織，若無則返回 None
    """
    headers = {
        "x-api-token": PIPEDRIVE_TOKEN,
        "Content-Type": "application/json"
    }
    
    # 優先使用統一編號搜尋
    if tax_id:
        params = {
            "term": tax_id,
            "fields": "custom_fields",  # 統一編號欄位
            "exact_match": "true",
            "limit": 1
        }
    elif name:
        params = {
            "term": name,
            "fields": "name",
            "exact_match": "true",
            "limit": 1
        }
    else:
        return None
    
    try:
        res = requests.get(
            f"{PIPEDRIVE_BASE}/organizations/search",
            params=params,
            headers=headers
        )
        res.raise_for_status()
        data = res.json()
        
        if data.get("success") and data.get("data") and len(data["data"]["items"]) > 0:
            return data["data"]["items"][0]["item"]
        return None
    except Exception as e:
        print(f"搜尋組織時發生錯誤: {e}")
        return None

def _logic_create_pipedrive_person(
    name: str,
    emails: Optional[List[str]] = None,
    phones: Optional[List[str]] = None,
    org_id: Optional[int] = None
):
    """
    建立一筆新的 Pipedrive 聯絡人（person）
    
    Args:
        name: 聯絡人姓名（必填）
        emails: 電子郵件列表，例如 ["user@example.com"]
        phones: 電話號碼列表，例如 ["+886912345678"]
        org_id: 關聯的組織 ID
    """
    payload = {
        "name": name
    }
    
    # API v2 使用 emails 和 phones（複數），並且需要陣列格式
    if emails is not None and len(emails) > 0:
        # 轉換為 API 需要的格式
        payload["emails"] = [ # type: ignore
            {
                "value": email,
                "primary": i == 0,  # 第一個設為主要
                "label": "work"
            }
            for i, email in enumerate(emails)
        ]
    
    if phones is not None and len(phones) > 0:
        payload["phones"] = [ # type: ignore
            {
                "value": phone,
                "primary": i == 0,
                "label": "work"
            }
            for i, phone in enumerate(phones)
        ]
    
    if org_id is not None:
        payload["org_id"] = org_id # type: ignore

    headers = {
        "x-api-token": PIPEDRIVE_TOKEN,
        "Content-Type": "application/json"
    }
    
    res = requests.post(f"{PIPEDRIVE_BASE}/persons", json=payload, headers=headers)

    try:
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": res.status_code,
            "response": res.text
        }

def _logic_create_pipedrive_organization(
    name: str,
    tax_id: Optional[str] = None,
    owner_id: Optional[int] = None,
    address: Optional[str] = None,
    visible_to: Optional[int] = None
):
    """
    建立一筆新的 Pipedrive 組織（organization）
    
    Args:
        name: 組織名稱（必填）
        owner_id: 擁有者的使用者 ID
        address: 組織地址
        visible_to: 可見性設定 (1=擁有者及關注者, 3=整個公司, 5=擁有者/關注者及其所屬群組, 7=整個公司)
    """
    payload = {
        "name": name
    }

    if tax_id is not None:
        payload["f47c12f460eac89b9db9352eb4b6deb381175fe6"] = tax_id
    
    if owner_id is not None:
        payload["owner_id"] = owner_id # type: ignore
    
    # API v2 中 address 需要特定格式（只有 value 是必填）
    if address is not None:
        payload["address"] = { # type: ignore
            "value": address
        }
    
    if visible_to is not None:
        payload["visible_to"] = visible_to # type: ignore

    headers = {
        "x-api-token": PIPEDRIVE_TOKEN,
        "Content-Type": "application/json"
    }
    
    res = requests.post(f"{PIPEDRIVE_BASE}/organizations", json=payload, headers=headers)

    try:
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": res.status_code,
            "response": res.text
        }

def _logic_get_or_create_person(
    person_name: str,
    person_email: Optional[str] = None,
    person_phone: Optional[str] = None,
    org_id: Optional[int] = None
) -> Optional[int]:
    """
    取得或建立聯絡人，返回 person_id
    優先使用 email 搜尋，確保不會重複建立相同 email 的聯絡人
    """
    # 先搜尋是否存在
    existing_person = search_pipedrive_person(name=person_name, email=person_email) # type: ignore
    
    if existing_person:
        print(f"找到現有聯絡人: {existing_person.get('name')} (ID: {existing_person.get('id')})")
        return existing_person.get("id")
    
    # 不存在則建立新聯絡人
    print(f"建立新聯絡人: {person_name}")
    emails = [person_email] if person_email else None
    phones = [person_phone] if person_phone else None
    
    new_person = _logic_create_pipedrive_person(
        name=person_name,
        emails=emails,
        phones=phones,
        org_id=org_id
    )
    
    if new_person and new_person.get("success"):
        new_person_data = new_person.get("data")
        if new_person_data:
            print(f"成功建立聯絡人 (ID: {new_person_data.get('id')})")
            return new_person_data.get("id")
    
    return None

def _logic_get_or_create_organization(
    org_name: str,
    org_tax_id: Optional[str] = None,
    org_address: Optional[str] = None
) -> Optional[int]:
    """
    取得或建立組織，返回 org_id
    優先使用統一編號搜尋，確保不會重複建立相同統編的組織
    """
    # 先搜尋是否存在
    existing_org = search_pipedrive_organization(org_name, org_tax_id) # type: ignore
    
    if existing_org:
        print(f"找到現有組織: {existing_org.get('name')} (ID: {existing_org.get('id')})")
        return existing_org.get("id")
    
    # 不存在則建立新組織
    print(f"建立新組織: {org_name}")
    new_org = _logic_create_pipedrive_organization(
        name=org_name,
        address=org_address
    )
    
    if new_org and new_org.get("success"):
        new_org_data = new_org.get("data")
        if new_org_data:
            print(f"成功建立組織 (ID: {new_org_data.get('id')})")
            return new_org_data.get("id")
    
    return None

# ==== MCP 工具 ====

@mcp.tool
def add_pipedrive_deal(
    title: str, 
    value: float,
    person_name: Optional[str] = None,
    person_email: Optional[str] = None,
    person_phone: Optional[str] = None,
    org_name: Optional[str] = None,
    org_tax_id: Optional[str] = None,
    org_address: Optional[str] = None, 
    ):
    """
    建立一筆新的 Pipedrive 交易（deal）
    
    此工具會自動處理聯絡人和組織：
    - 如果指定的聯絡人或組織已存在，會直接使用
    - 如果不存在，會自動建立新的聯絡人或組織
    - 聯絡人搜尋優先使用 email（更精確），避免重複建立
    - 組織搜尋優先使用統一編號（更精確），避免重複建立
    
    Args:
        title: 交易標題（必填）
        value: 交易金額 (必填)
        person_name: 聯絡人姓名（選填）
        person_email: 聯絡人電子郵件（選填，強烈建議提供以避免重複建立）
        person_phone: 聯絡人電話（選填）
        org_name: 組織名稱（選填）
        org_tax_id: 組織統一編號（選填，強烈建議提供以避免重複建立）
        org_address: 組織地址（選填）
    
    Returns:
        包含交易詳細資訊的字典，或錯誤訊息
    """

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        numeric_value = 0
    
    # 處理組織
    org_id = None
    if org_name:
        org_id = _logic_get_or_create_organization(org_name, org_tax_id, org_address)
        if org_id is None:
            return {
                "error": f"無法取得或建立組織: {org_name}",
                "success": False
            }
    
    # 處理聯絡人（如果有組織，將聯絡人關聯到組織）
    person_id = None
    if person_name:
        person_id = _logic_get_or_create_person(
            person_name=person_name,
            person_email=person_email,
            person_phone=person_phone,
            org_id=org_id
        )
        if person_id is None:
            return {
                "error": f"無法取得或建立聯絡人: {person_name}",
                "success": False
            }
    
    # 建立交易
    payload = {
        "title": title,
        "value": numeric_value,
        "org_id": org_id,
        "person_id": person_id
    }

    headers = {
        "x-api-token": PIPEDRIVE_TOKEN,
        "Content-Type": "application/json"
    }
    
    res = requests.post(f"{PIPEDRIVE_BASE}/deals", json=payload, headers=headers)
    

    try:
        res.raise_for_status()
        result = res.json()

        deal_id = result["data"]["id"]
        
        # 添加額外資訊
        result["deal_url"] = f"https://{PIPEDRIVE_DOMAIN}.pipedrive.com/deal/{deal_id}"
        result["created_organization"] = org_name if org_name and org_id else None
        result["created_person"] = person_name if person_name and person_id else None
        
        return result
    except requests.exceptions.RequestException as e:
        return {
            "error": str(e),
            "status_code": res.status_code,
            "response": res.text,
            "success": False
        }



if __name__ == "__main__":
    asyncio.run(mcp.run(transport="http", host="0.0.0.0", port=8080)) # type: ignore





