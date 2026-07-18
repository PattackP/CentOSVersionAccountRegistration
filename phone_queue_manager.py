# -*- coding: utf-8 -*-
# phone_queue_manager.py
# 手机号队列管理模块
import queue
from threading import Lock
from feishu_api import _fetch_feishu_sheet_data

# ---------------- 配置 ----------------
PHONE_SHEET_ID = "253571"
PHONE_SPREADSHEET_TOKEN = "TX74w2JYPia8ZJk8Lmdc279vn0g"

# ---------------- 队列定义 ----------------
phone_queue = queue.Queue()
phone_queue_lock = Lock()


def load_phone_queue():
    """
    从飞书表格加载数据到队列
    读取范围：A:E列，从第2行开始到有数据的最后一行
    A列:行号 B列:sheetid C列:spreadsheetToken D列:手机号码 E列:接码链接
    """
    # 清空现有队列
    with phone_queue_lock:
        while not phone_queue.empty():
            phone_queue.get()

    print(f"ℹ️  开始加载手机号队列 - 表格: {PHONE_SHEET_ID}")

    data = _fetch_feishu_sheet_data(PHONE_SHEET_ID, PHONE_SPREADSHEET_TOKEN, "A:E")

    if not data or len(data) < 2:
        print("⚠️  表格为空或没有数据行")
        return 0

    count = 0
    skip_count = 0
    for row in data[1:]:  # 跳过表头
        if not row or len(row) < 5:
            print(f"⚠️  跳过行（列数不足）: {row}")
            continue

        # 检查是否有有效数据（至少手机号码不能为空）
        phone_number = str(row[3]).strip() if len(row) > 3 else ""
        if not phone_number or phone_number == "None":
            continue

        # 美国号码去掉开头的1
        if phone_number.startswith("1"):
            phone_number = phone_number[1:]

        # 处理 sms_url（飞书超链接格式）
        raw_sms_url = row[4] if len(row) > 4 else ""
        sms_url = ""

        if isinstance(raw_sms_url, list):
            # 飞书超链接格式：[{'link': 'https://...', 'text': 'https://...', 'type': 'url'}]
            if len(raw_sms_url) > 0 and isinstance(raw_sms_url[0], dict):
                sms_url = raw_sms_url[0].get('link', '') or raw_sms_url[0].get('text', '')
        elif isinstance(raw_sms_url, str):
            sms_url = raw_sms_url.strip()

        sms_url = sms_url.strip('`').strip()
        print(f"ℹ️  行号={row[0]}, 手机号={phone_number}, sms_url={sms_url}")

        if not sms_url.startswith("https://api.68sms.com/api/sms/get?key="):
            print(f"⚠️  跳过（sms_url格式不符）: {sms_url[:50]}...")
            skip_count += 1
            continue

        item = {
            "row_num": str(row[0]).strip() if len(row) > 0 else "",
            "sheetid": str(row[1]).strip() if len(row) > 1 else "",
            "spreadsheettoken": str(row[2]).strip() if len(row) > 2 else "",
            "phone_number": phone_number,
            "sms_url": sms_url
        }

        with phone_queue_lock:
            phone_queue.put(item)
        count += 1

    print(f"✅ 手机号队列加载完成 - 共加载 {count} 条数据，跳过 {skip_count} 条")
    return count


def get_phone_data():
    """
    从队列取出一条数据（FIFO）
    取出后数据从队列中移除
    """
    with phone_queue_lock:
        try:
            return phone_queue.get(block=False)
        except queue.Empty:
            return None


def put_back_phone_data(row_num, sheetid, spreadsheettoken, phone_number, sms_url):
    """
    把取出但未消费成功的数据放回队列
    """
    item = {
        "row_num": row_num,
        "sheetid": sheetid,
        "spreadsheettoken": spreadsheettoken,
        "phone_number": phone_number,
        "sms_url": sms_url
    }

    with phone_queue_lock:
        phone_queue.put(item)

    print(f"✅ 数据已放回队列 - 行号: {row_num}, 手机号: {phone_number}")
    return True


def get_phone_queue_status():
    """
    获取队列状态
    """
    with phone_queue_lock:
        size = phone_queue.qsize()
        return {
            "queue_size": size,
            "is_empty": size == 0
        }
