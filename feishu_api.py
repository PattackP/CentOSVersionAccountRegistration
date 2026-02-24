# -*- coding: utf-8 -*-
import requests
from token_manager import get_valid_feishu_token
from config import FEISHU_RANGE_STR

# ---------------- 飞书API 基础服务 ----------------

def _fetch_feishu_sheet_data(sheet_id, spreadsheet_token, range_str=None):
    """
    通用：读取飞书表格数据
    :param range_str: 如果为None，使用默认FEISHU_RANGE_STR，否则使用传入的range_str (e.g. "A:J")
    """
    actual_range = range_str if range_str else FEISHU_RANGE_STR
    full_range = f"{sheet_id}!{actual_range}"
    api_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{full_range}"

    access_token = get_valid_feishu_token(token_type="tenant_access_token")
    if not access_token:
        print("❌ 无法获取飞书有效Token，加载表格失败")
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        if result.get("code") != 0:
            print(f"❌ 飞书接口报错：{result.get('msg')}（错误码：{result.get('code')}）")
            return None
        return result.get("data", {}).get("valueRange", {}).get("values", [])
    except Exception as e:
        print(f"❌ 调用飞书接口失败：{str(e)}")
        return None

def update_feishu_sheet_cell(sheet_id, spreadsheet_token, cell_range, content):
    """
    更新飞书表格指定单元格内容（严格遵循飞书v2单个范围写入接口文档）
    :param cell_range: 单元格范围（例："3eb130!J2:J2"，符合文档格式 <sheetId>!<开始>:<结束>）
    :param content: 要写入的内容
    """
    api_url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values"
    access_token = get_valid_feishu_token(token_type="tenant_access_token")

    if not access_token:
        print("❌ 无法获取飞书有效Token，更新表格失败")
        return False

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    request_body = {
        "valueRange": {
            "range": cell_range,
            "values": [[content]]
        }
    }

    try:
        response = requests.put(api_url, json=request_body, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        if result.get("code") != 0:
            print(f"❌ 飞书表格更新失败：{result.get('msg')}（错误码：{result.get('code')}）")
            return False

        data = result.get("data", {})
        print(f"✅ 飞书表格单元格{cell_range}更新成功！")
        print(f"   修订版本：{data.get('revision')}，更新单元格数：{data.get('updatedCells')}")
        return True
    except Exception as e:
        print(f"❌ 调用飞书表格更新接口失败：{str(e)}")
        return False
