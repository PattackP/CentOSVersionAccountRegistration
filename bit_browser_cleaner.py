# -*- coding: utf-8 -*-
import requests
import os

try:
    from config import FEISHU_FIXED_SHEETS
    from feishu_api import _fetch_feishu_sheet_data
    from token_manager import get_valid_feishu_token
except ImportError as e:
    print(f"❌ 错误：无法从项目导入模块：{e}")
    print("   请确保此脚本与 config.py、feishu_api.py、token_manager.py 在同一个项目目录下。")
    FEISHU_FIXED_SHEETS = []

TIMEOUT_STATUSES = {
    "等待注册链接超时",
    "验证码页面等待超时",
    "账号输入框页面等待超时"
}

BIT_API_URL = "http://127.0.0.1:55055/browser/close/byseqs"

def close_bit_windows(window_ids):
    if not window_ids:
        return

    int_ids = []
    for an_id in window_ids:
        try:
            int_ids.append(int(an_id))
        except (ValueError, TypeError):
            continue

    if not int_ids:
        return

    headers = {"Content-Type": "application/json"}
    payload = {"seqs": int_ids}

    try:
        response = requests.post(BIT_API_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and 'success' in response.text.lower():
             print(f"✅ 成功关闭 {len(int_ids)} 个比特浏览器窗口")
    except requests.RequestException:
        pass

def batch_clear_sheet_rows(spreadsheet_token, sheet_id, row_numbers):
    if not row_numbers:
        return

    access_token = get_valid_feishu_token(token_type="tenant_access_token")
    if not access_token:
        return

    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    value_ranges = []
    for row_num in row_numbers:
        value_ranges.append({
            "range": f"{sheet_id}!G{row_num}:G{row_num}",
            "values": [[""]]
        })
        value_ranges.append({
            "range": f"{sheet_id}!H{row_num}:H{row_num}",
            "values": [[""]]
        })
        value_ranges.append({
            "range": f"{sheet_id}!J{row_num}:J{row_num}",
            "values": [[""]]
        })

    payload = {"valueRanges": value_ranges}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        if data.get("code") == 0:
            print(f"✅ 表格 {sheet_id}: 清空了 {len(row_numbers)} 行的 G、H、J 列")
    except requests.RequestException:
        pass

def reset_unauthorized_accounts():
    try:
        url = "http://112.74.43.109:5000/reset_unauthorized_accounts"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("✅ 成功调用 reset_unauthorized_accounts 接口")
        else:
            print(f"⚠️  reset_unauthorized_accounts 接口返回状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"⚠️  调用 reset_unauthorized_accounts 失败: {e}")

def main():
    print("\n--- 比特浏览器超时窗口清理工具 ---")

    reset_unauthorized_accounts()

    if not FEISHU_FIXED_SHEETS:
        print("\n❌ 配置加载失败，程序已终止")
        return

    all_window_ids_to_close = []
    sheets_rows_map = {}

    for sheet_info in FEISHU_FIXED_SHEETS:
        spreadsheet_token = sheet_info["spreadsheet_token"]
        sheet_id = sheet_info["sheet_id"]
        sheet_key = (spreadsheet_token, sheet_id)

        data = _fetch_feishu_sheet_data(sheet_id, spreadsheet_token, "A:J")

        if not data or len(data) < 2:
            continue

        for i, row in enumerate(data[1:]):
            if len(row) < 10:
                continue

            status = str(row[9]).strip() if len(row) > 9 else ""
            window_id = str(row[7]).strip() if len(row) > 7 else ""

            if status in TIMEOUT_STATUSES and window_id:
                row_num = i + 2
                all_window_ids_to_close.append(window_id)
                if sheet_key not in sheets_rows_map:
                    sheets_rows_map[sheet_key] = []
                sheets_rows_map[sheet_key].append(row_num)

    if not all_window_ids_to_close:
        print("未发现超时窗口")
        return

    print(f"找到 {len(all_window_ids_to_close)} 个超时窗口")
    close_bit_windows(all_window_ids_to_close)

    for (spreadsheet_token, sheet_id), row_numbers in sheets_rows_map.items():
        batch_clear_sheet_rows(spreadsheet_token, sheet_id, row_numbers)

    print("\n--- 清理任务结束 ---")

if __name__ == "__main__":
    main()
