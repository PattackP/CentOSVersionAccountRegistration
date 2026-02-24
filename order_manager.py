# -*- coding: utf-8 -*-
import queue
import re
import random
from threading import Lock
from models import Order
from feishu_api import _fetch_feishu_sheet_data

# ---------------- 订单队列管理 ----------------

order_queue = queue.Queue()
order_queue_lock = Lock()

# 订单相关随机数据配置
COMMON_FIRST_NAMES = [
    "Emma", "Olivia", "Ava", "Sophia", "Isabella", "Charlotte", "Amelia", "Mia",
    "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Ella", "Avery", "Sofia",
    "Grace", "Chloe", "Victoria", "Riley", "Zoey", "Nora", "Lily", "Zoe", "Hannah",
    "Layla", "Scarlett", "Aria", "Ellie", "Natalie", "Addison", "Brooklyn", "Lucy",
    "Skylar", "Penelope", "Claire", "Violet", "Luna", "Everly", "Audrey", "Bella",
    "Nova", "Emilia", "Stella", "Hazel", "Willow", "Paisley", "Aubrey", "Aaliyah",
    "Savannah", "Leah", "Eleanor", "Madison", "Peyton", "Camila", "Gianna", "Maya",
    "Evangeline", "Lillian", "Naomi", "Elena",
    "Liam", "Noah", "Elijah", "Lucas", "Mason", "Ethan", "Oliver", "Benjamin",
    "Theodore", "Jacob", "Michael", "Alexander", "Jackson", "Daniel", "Matthew",
    "Aiden", "Wyatt", "Lucas", "Leo", "Owen", "Samuel", "Jack", "Henry", "Ezra",
    "Isaac", "Sebastian", "Carter", "Julian", "Grayson", "Levi", "Ryan", "Elias",
    "Asher", "Jaxon", "Gabriel", "Nathan", "Caleb", "Logan", "Connor", "Hunter",
    "Adrian", "Thomas", "Aaron", "Charles", "David", "Ezekiel", "Joshua", "Luke",
    "Miles", "Nicholas", "Oliver", "Patrick", "Quinn", "Robert", "Silas", "Tyler",
    "Ulysses", "Victor", "William", "Xavier"
]

COMMON_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis",
    "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott",
    "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson",
    "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Perez", "Edwards",
    "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook",
    "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Richardson",
    "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez",
    "James", "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett",
    "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins", "Perry",
    "Powell", "Long", "Patterson", "Hughes", "Foster", "Gonzales", "Bryant",
    "Alexander", "Russell", "Griffin", "Diaz", "Hayes", "Myers", "Ford",
    "Hamilton", "Graham", "Sullivan", "Wallace", "Woods", "Cole", "West",
    "Jordan", "Owens", "Reynolds", "Fisher", "Ellis", "Harrison", "Gibson"
]

def _get_random_first_name():
    return random.choice(COMMON_FIRST_NAMES)

def _get_random_last_name():
    return random.choice(COMMON_LAST_NAMES)

def _generate_realistic_us_phone():
    area_code = random.randint(100, 999)
    prefix = random.randint(100, 999)
    line_number = random.randint(1000, 9999)
    return f"{area_code}{prefix}{line_number}"

def _split_sku(sku_str):
    if not sku_str:
        return ("", "")
    sku_parts = [part.strip() for part in sku_str.split(",")]
    color = sku_parts[0] if len(sku_parts) >= 1 else ""
    size = sku_parts[1] if len(sku_parts) >= 2 else ""
    return (color, size)

def _extract_pure_url(link_str):
    if not link_str:
        return ""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    match = re.search(url_pattern, str(link_str))
    return match.group() if match else str(link_str).strip()

def _load_order_with_empty_window_column(sheet_data):
    if not sheet_data or len(sheet_data) < 2:
        return 0

    valid_order_count = 0
    ROW_DUPLICATE_TIMES = 5

    valid_orders = []

    for row_idx, row_data in enumerate(sheet_data[1:]):
        if len(row_data) < 14:
            print(f"⚠️ 第{row_idx+2}行数据列数不足（仅{len(row_data)}列），跳过")
            continue

        window_num_data = str(row_data[13]).strip() if row_data[13] is not None else ""
        if window_num_data:
            print(f"⚠️ 第{row_idx+2}行N列数据不为空，跳过")
            continue

        try:
            sheetid = str(row_data[1]).strip() if row_data[1] is not None else ""
            spreadsheet_token = str(row_data[2]).strip() if row_data[2] is not None else ""
            order_id = str(row_data[3]).strip() if row_data[3] is not None else ""
            link_pure = _extract_pure_url(str(row_data[4]).strip() if row_data[4] is not None else "")
            sku_color, sku_size = _split_sku(str(row_data[5]).strip() if row_data[5] is not None else "")
            address = str(row_data[8]).strip() if row_data[8] is not None else ""
            city = str(row_data[10]).strip() if row_data[10] is not None else ""
            state = str(row_data[11]).strip() if row_data[11] is not None else ""
            zip_code = str(row_data[12]).strip() if row_data[12] is not None else ""
            
            order_data = {
                "row_num": row_data[0],
                "sheetid": sheetid,
                "spreadsheet_token": spreadsheet_token,
                "order_id": order_id,
                "link_pure": link_pure,
                "sku_color": sku_color,
                "sku_size": sku_size,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code
            }
            valid_orders.append(order_data)
            print(f"ℹ️  第{row_idx+2}行数据已解析，准备加载")
        except Exception as e:
            print(f"⚠️ 第{row_idx+2}行数据预处理失败：{str(e)}，跳过")
            continue

    for round_num in range(1, ROW_DUPLICATE_TIMES + 1):
        print(f"🔄 开始第 {round_num}/{ROW_DUPLICATE_TIMES} 轮加载...")
        for order_data in valid_orders:
            try:
                new_order = Order(
                    row_num=order_data["row_num"],
                    sheetid=order_data["sheetid"],
                    spreadsheet_token=order_data["spreadsheet_token"],
                    order_id=order_data["order_id"],
                    link=order_data["link_pure"],
                    sku_color=order_data["sku_color"],
                    sku_size=order_data["sku_size"],
                    first_name=_get_random_first_name(),
                    last_name=_get_random_last_name(),
                    address=order_data["address"],
                    phone=_generate_realistic_us_phone(),
                    city=order_data["city"],
                    state=order_data["state"],
                    zip_code=order_data["zip_code"],
                    window_num=""
                )
                order_queue.put(new_order)
                valid_order_count += 1
            except Exception as e:
                print(f"⚠️ 订单解析失败：{str(e)}，跳过")
                continue
        print(f"✅ 第 {round_num}/{ROW_DUPLICATE_TIMES} 轮加载完成")

    print(f"📊 共解析 {len(valid_orders)} 个有效订单，循环加载 {ROW_DUPLICATE_TIMES} 轮，总计 {valid_order_count} 条")
    return valid_order_count

def reinit_order_queue_from_feishu(sheet_id, spreadsheet_token):
    """重新初始化订单队列（传参模式，加载指定表格）"""
    with order_queue_lock:
        while not order_queue.empty():
            try:
                order_queue.get(block=False)
            except queue.Empty:
                break
        print(f"ℹ️  原有订单队列已清空，准备重新初始化指定表格（sheet_id: {sheet_id}）数据")

        sheet_data = _fetch_feishu_sheet_data(sheet_id=sheet_id, spreadsheet_token=spreadsheet_token)
        if not sheet_data:
            print(f"❌ 指定表格（sheet_id: {sheet_id}）数据为空/格式错误，无法重新初始化订单队列")
            return False

        valid_order_count = _load_order_with_empty_window_column(sheet_data)
        print(f"✅ 指定表格订单重新初始化完成！共加载 {valid_order_count} 条有效订单")
        return True

def get_order_queue_status():
    with order_queue_lock:
        return {
            'queue_size': order_queue.qsize(),
            'is_empty': order_queue.empty()
        }

def get_order_and_remaining():
    with order_queue_lock:
        try:
            order = order_queue.get(block=False)
            remaining = order_queue.qsize()
            return (order, remaining)
        except queue.Empty:
            return (None, 0)

def load_order_from_specified_sheet(sheet_id, spreadsheet_token):
    """加载指定表格订单"""
    with order_queue_lock:
        while not order_queue.empty():
            try:
                order_queue.get(block=False)
            except queue.Empty:
                break
        print(f"ℹ️  原有订单队列已清空，准备加载指定表格（sheet_id: {sheet_id}）数据")

        sheet_data = _fetch_feishu_sheet_data(sheet_id=sheet_id, spreadsheet_token=spreadsheet_token)
        if not sheet_data:
            print(f"❌ 指定表格（sheet_id: {sheet_id}）数据为空/格式错误，无法加载订单队列")
            return False

        valid_order_count = _load_order_with_empty_window_column(sheet_data)
        print(f"✅ 指定表格订单加载完成！共加载 {valid_order_count} 条有效订单")
        return True
