from fastmcp import FastMCP
from typing import Optional, List

import requests
import os
import asyncio

PIPEDRIVE_TOKEN = "b8928b87616ec392587b44268757fa8b9353a95b"
PIPEDRIVE_BASE = "https://api.pipedrive.com/api/v2"

mcp = FastMCP("chatgpt-pd-operation")

@mcp.tool
def add_pipedrive_deal(title: str, value: float, org_id: Optional[int] = None, person_id: Optional[int] = None):
    """
    建立一筆新的 Pipedrive 交易（deal）
    """

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        numeric_value = 0

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

    # 錯誤處理
    try:
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "response": res.text}

# === 建立聯絡人（Person） ===
@mcp.tool
def add_pipedrive_person(
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

# === 建立組織（Organisation） ===
@mcp.tool
def add_pipedrive_organization(
    name: str,
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

if __name__ == "__main__":
    asyncio.run(mcp.run(transport="http", host="0.0.0.0", port=8080)) # type: ignore





