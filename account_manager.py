# -*- coding: utf-8 -*-
import queue
from threading import Lock
from models import Account
from feishu_api import _fetch_feishu_sheet_data
from token_manager import get_valid_feishu_token
from config import FEISHU_FIXED_SHEETS

# ---------------- 账户队列管理 ----------------

# Authorized 队列: 存储 "该号是0.99" 的账户
authorized_account_queue = queue.Queue()
authorized_account_queue_lock = Lock()
loaded_authorized_emails = set()
loaded_authorized_emails_lock = Lock()

# Unauthorized 队列: 存储 "H列不为空" 且 "J列不是0.99" 的账户
unauthorized_account_queue = queue.Queue()
unauthorized_account_queue_lock = Lock()
loaded_unauthorized_emails = set()
loaded_unauthorized_emails_lock = Lock()

# Offline 队列: 存储 "J列='使用过程中被弹出'" 的账户
offline_account_queue = queue.Queue()
offline_account_queue_lock = Lock()
loaded_offline_emails = set()
loaded_offline_emails_lock = Lock()


def _fetch_feishu_account_sheet_data(sheet_id, spreadsheet_token):
    """读取未认证账户飞书表格数据（包含J列流程追踪）"""
    return _fetch_feishu_sheet_data(sheet_id, spreadsheet_token, range_str="A:J")

def _parse_email_field(raw_email):
    """解析邮箱字段，处理飞书富文本链接对象或字符串，并移除 mailto: 前缀"""
    email_account = ""
    if isinstance(raw_email, list) and len(raw_email) > 0 and isinstance(raw_email[0], dict):
        # 提取链接或文本
        item = raw_email[0]
        email_account = item.get('link') or item.get('text') or ""
    elif isinstance(raw_email, str):
        # 尝试处理被字符串化的列表（以防万一数据源已经是字符串）
        s_email = raw_email.strip()
        if s_email.startswith("[{'") and ("'link':" in s_email or "'text':" in s_email):
            try:
                import ast
                parsed = ast.literal_eval(s_email)
                if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                    email_account = parsed[0].get('link') or parsed[0].get('text') or ""
                else:
                    email_account = s_email
            except:
                email_account = s_email
        else:
            email_account = s_email
    else:
        email_account = str(raw_email).strip() if raw_email else ""
    
    # 移除 mailto: 前缀
    if email_account.lower().startswith("mailto:"):
        email_account = email_account[7:]
        
    return email_account

def _parse_account_row(row_data, sheet_id, row_idx):
    try:
        row_num = str(row_data[0]).strip() if row_data[0] else ""
        sheetid = str(row_data[1]).strip() if row_data[1] else ""
        
        # 处理 D列 (邮箱账号)
        email_account = _parse_email_field(row_data[3])

        email_password = str(row_data[4]).strip() if row_data[4] else ""
        env = str(row_data[5]).strip() if row_data[5] else ""
        proxy_address = str(row_data[6]).strip() if row_data[6] else ""
        window_id = str(row_data[7]).strip() if row_data[7] else ""
        process_tracking = str(row_data[9]).strip() if row_data[9] is not None else ""
        
        return {
            "row_num": row_num,
            "sheetid": sheetid,
            "email_account": email_account,
            "email_password": email_password,
            "env": env,
            "proxy_address": proxy_address,
            "window_id": window_id,
            "process_tracking": process_tracking
        }
    except Exception as e:
        print(f"⚠️ 账户表格{sheet_id}第{row_idx+2}行预处理失败：{str(e)}，跳过")
        return None

def _load_authorized_account_data(sheet_data, sheet_id, spreadsheet_token):
    if not sheet_data or len(sheet_data) < 2: return 0
    valid_count = 0
    
    for row_idx, row_data in enumerate(sheet_data[1:]):
        if len(row_data) < 10: continue
        
        account_info = _parse_account_row(row_data, sheet_id, row_idx)
        if not account_info: continue
        
        if not account_info["email_account"]: continue
        if not account_info["window_id"]: continue
        
        # 核心过滤：必须是 "该号是0.99"
        if account_info["process_tracking"] != "该号是0.99":
            continue
            
        with loaded_authorized_emails_lock:
            if account_info["email_account"] in loaded_authorized_emails:
                continue
                
        try:
            new_account = Account(
                row_num=account_info["row_num"],
                sheetid=account_info["sheetid"],
                spreadsheet_token=spreadsheet_token,
                email_account=account_info["email_account"],
                email_password=account_info["email_password"],
                env=account_info["env"],
                proxy_address=account_info["proxy_address"],
                window_id=account_info["window_id"]
            )
            with authorized_account_queue_lock:
                authorized_account_queue.put(new_account)
            with loaded_authorized_emails_lock:
                loaded_authorized_emails.add(account_info["email_account"])
            valid_count += 1
            print(f"✅ [Authorized] 账户{account_info['email_account']}加入队列（表格{sheet_id}第{row_idx+2}行）")
        except Exception as e:
            print(f"⚠️ 加载失败：{str(e)}")
            continue
            
    return valid_count

def _load_unauthorized_account_data(sheet_data, sheet_id, spreadsheet_token):
    if not sheet_data or len(sheet_data) < 2: return 0
    valid_count = 0
    
    for row_idx, row_data in enumerate(sheet_data[1:]):
        if len(row_data) < 10: continue
        
        account_info = _parse_account_row(row_data, sheet_id, row_idx)
        if not account_info: continue
        
        if not account_info["email_account"]: continue
        if not account_info["window_id"]: continue
        
        # 核心过滤：排除 "该号是0.99"
        if account_info["process_tracking"] == "该号是0.99":
            continue
            
        with loaded_unauthorized_emails_lock:
            if account_info["email_account"] in loaded_unauthorized_emails:
                continue
                
        try:
            new_account = Account(
                row_num=account_info["row_num"],
                sheetid=account_info["sheetid"],
                spreadsheet_token=spreadsheet_token,
                email_account=account_info["email_account"],
                email_password=account_info["email_password"],
                env=account_info["env"],
                proxy_address=account_info["proxy_address"],
                window_id=account_info["window_id"]
            )
            with unauthorized_account_queue_lock:
                unauthorized_account_queue.put(new_account)
            with loaded_unauthorized_emails_lock:
                loaded_unauthorized_emails.add(account_info["email_account"])
            valid_count += 1
            print(f"✅ [Unauthorized] 账户{account_info['email_account']}加入队列（表格{sheet_id}第{row_idx+2}行）")
        except Exception as e:
            print(f"⚠️ 加载失败：{str(e)}")
            continue
            
    return valid_count

def load_all_authorized_accounts():
    total = 0
    with authorized_account_queue_lock:
        if authorized_account_queue.empty():
            with loaded_authorized_emails_lock:
                loaded_authorized_emails.clear()
            print("ℹ️  Authorized队列为空，已重置去重记录")

    for sheet_info in FEISHU_FIXED_SHEETS:
        sheet_id = sheet_info["sheet_id"]
        token = sheet_info["spreadsheet_token"]
        print(f"ℹ️  [Authorized] 扫描表格{sheet_id}...")
        data = _fetch_feishu_account_sheet_data(sheet_id, token)
        if data:
            count = _load_authorized_account_data(data, sheet_id, token)
            total += count
    return total

def load_all_unauthorized_accounts():
    total = 0
    with unauthorized_account_queue_lock:
        if unauthorized_account_queue.empty():
            with loaded_unauthorized_emails_lock:
                loaded_unauthorized_emails.clear()
            print("ℹ️  Unauthorized队列为空，已重置去重记录")

    for sheet_info in FEISHU_FIXED_SHEETS:
        sheet_id = sheet_info["sheet_id"]
        token = sheet_info["spreadsheet_token"]
        print(f"ℹ️  [Unauthorized] 扫描表格{sheet_id}...")
        data = _fetch_feishu_account_sheet_data(sheet_id, token)
        if data:
            count = _load_unauthorized_account_data(data, sheet_id, token)
            total += count
    return total

def load_unauthorized_accounts_from_sheet(sheet_id, spreadsheet_token):
    """加载指定表格的未认证账户到队列"""
    print(f"ℹ️  [Unauthorized] 加载指定表格 {sheet_id}...")
    data = _fetch_feishu_account_sheet_data(sheet_id, spreadsheet_token)
    if not data:
        print(f"❌ 指定表格 {sheet_id} 数据为空或获取失败")
        return 0
    
    count = _load_unauthorized_account_data(data, sheet_id, spreadsheet_token)
    print(f"✅ 指定表格 {sheet_id} 加载完成，共 {count} 个未认证账户")
    return count

def load_single_authorized_account(sheet_id, spreadsheet_token, row_num):
    # 手动加载，重用底层 fetch 逻辑会更干净，但这里需要特定的一行
    # 直接调用 feishu_api 的 fetch，但传入特定 range
    full_range_str = f"A{row_num}:J{row_num}"
    
    # 这里我们不调用 _fetch_feishu_sheet_data 因为它拼接了 sheet_id!range
    # 但是 _fetch_feishu_sheet_data 也是接收 range_str 参数的
    
    # 稍微修改下逻辑，直接复用代码
    # 调用 feishu_api
    values = _fetch_feishu_sheet_data(sheet_id, spreadsheet_token, range_str=full_range_str)
    
    if values is None: # 报错了
        return False, "飞书接口调用失败"
    
    if not values or not values[0]:
        return False, "指定行数据为空"
        
    row_data = values[0]
    while len(row_data) < 10:
        row_data.append("")
        
    try:
        r_num = str(row_data[0]).strip() if row_data[0] else str(row_num)
        s_id = str(row_data[1]).strip() if row_data[1] else sheet_id
        email_account = _parse_email_field(row_data[3])
        email_password = str(row_data[4]).strip() if row_data[4] else ""
        env = str(row_data[5]).strip() if row_data[5] else ""
        proxy_address = str(row_data[6]).strip() if row_data[6] else ""
        window_id = str(row_data[7]).strip() if row_data[7] else ""
    except Exception as e:
        return False, f"数据解析异常：{str(e)}"

    if not email_account:
        return False, "邮箱账号为空"

    with loaded_authorized_emails_lock:
        if email_account in loaded_authorized_emails:
            print(f"ℹ️  注意：账户{email_account}已在加载记录中，正在手动重新加载...")
        else:
            loaded_authorized_emails.add(email_account)

    new_account = Account(
        row_num=r_num,
        sheetid=s_id,
        spreadsheet_token=spreadsheet_token,
        email_account=email_account,
        email_password=email_password,
        env=env,
        proxy_address=proxy_address,
        window_id=window_id
    )

    with authorized_account_queue_lock:
        authorized_account_queue.put(new_account)
        
    print(f"✅ 指定账户{email_account}已成功加入 Authorized 队列（表格{s_id}第{r_num}行）")
    return True, f"账户{email_account}加载成功"

def get_authorized_account():
    with authorized_account_queue_lock:
        try:
            return authorized_account_queue.get(block=False)
        except queue.Empty:
            return None

def get_unauthorized_account():
    with unauthorized_account_queue_lock:
        try:
            return unauthorized_account_queue.get(block=False)
        except queue.Empty:
            return None

def get_authorized_queue_status():
    with authorized_account_queue_lock:
        return {
            'queue_size': authorized_account_queue.qsize(),
            'is_empty': authorized_account_queue.empty()
        }

def get_unauthorized_queue_status():
    with unauthorized_account_queue_lock:
        return {
            'queue_size': unauthorized_account_queue.qsize(),
            'is_empty': unauthorized_account_queue.empty()
        }

def get_account_queue_status():
    return get_authorized_queue_status()

def reset_authorized_queue_and_emails():
    with authorized_account_queue_lock:
        while not authorized_account_queue.empty():
            try:
                authorized_account_queue.get(block=False)
            except queue.Empty: break
    with loaded_authorized_emails_lock:
        loaded_authorized_emails.clear()
    print("✅ Authorized 账户队列和已加载邮箱记录已重置")

def reset_unauthorized_queue_and_emails():
    with unauthorized_account_queue_lock:
        while not unauthorized_account_queue.empty():
            try:
                unauthorized_account_queue.get(block=False)
            except queue.Empty: break
    with loaded_unauthorized_emails_lock:
        loaded_unauthorized_emails.clear()
    print("✅ Unauthorized 账户队列和已加载邮箱记录已重置")

def _load_offline_account_data(sheet_data, sheet_id, spreadsheet_token):
    """加载离线账户数据（J列='使用过程中被弹出'）"""
    if not sheet_data or len(sheet_data) < 2: return 0
    valid_count = 0
    
    for row_idx, row_data in enumerate(sheet_data[1:]):
        if len(row_data) < 10: continue
        
        account_info = _parse_account_row(row_data, sheet_id, row_idx)
        if not account_info: continue
        
        if not account_info["email_account"]: continue
        if not account_info["window_id"]: continue
        
        if account_info["process_tracking"] != "使用过程中被弹出":
            continue
            
        with loaded_offline_emails_lock:
            if account_info["email_account"] in loaded_offline_emails:
                continue
                
        try:
            new_account = Account(
                row_num=account_info["row_num"],
                sheetid=account_info["sheetid"],
                spreadsheet_token=spreadsheet_token,
                email_account=account_info["email_account"],
                email_password=account_info["email_password"],
                env=account_info["env"],
                proxy_address=account_info["proxy_address"],
                window_id=account_info["window_id"]
            )
            with offline_account_queue_lock:
                offline_account_queue.put(new_account)
            with loaded_offline_emails_lock:
                loaded_offline_emails.add(account_info["email_account"])
            valid_count += 1
            print(f"✅ [Offline] 账户{account_info['email_account']}加入队列（表格{sheet_id}第{row_idx+2}行）")
        except Exception as e:
            print(f"⚠️ 加载失败：{str(e)}")
            continue
            
    return valid_count

def load_all_offline_accounts():
    """加载所有表格的离线账户"""
    total = 0
    with offline_account_queue_lock:
        if offline_account_queue.empty():
            with loaded_offline_emails_lock:
                loaded_offline_emails.clear()
            print("ℹ️  Offline队列为空，已重置去重记录")

    for sheet_info in FEISHU_FIXED_SHEETS:
        sheet_id = sheet_info["sheet_id"]
        token = sheet_info["spreadsheet_token"]
        print(f"ℹ️  [Offline] 扫描表格{sheet_id}...")
        data = _fetch_feishu_account_sheet_data(sheet_id, token)
        if data:
            count = _load_offline_account_data(data, sheet_id, token)
            total += count
    return total

def load_offline_accounts_from_sheet(sheet_id, spreadsheet_token):
    """加载指定表格的离线账户到队列"""
    print(f"ℹ️  [Offline] 加载指定表格 {sheet_id}...")
    data = _fetch_feishu_account_sheet_data(sheet_id, spreadsheet_token)
    if not data:
        print(f"❌ 指定表格 {sheet_id} 数据为空或获取失败")
        return 0
    
    count = _load_offline_account_data(data, sheet_id, spreadsheet_token)
    print(f"✅ 指定表格 {sheet_id} 加载完成，共 {count} 个离线账户")
    return count

def get_offline_account():
    """获取一个离线账户"""
    with offline_account_queue_lock:
        try:
            return offline_account_queue.get(block=False)
        except queue.Empty:
            return None

def get_offline_queue_status():
    """获取离线账户队列状态"""
    with offline_account_queue_lock:
        return {
            'queue_size': offline_account_queue.qsize(),
            'is_empty': offline_account_queue.empty()
        }

def reset_offline_queue_and_emails():
    """重置离线账户队列和去重记录"""
    with offline_account_queue_lock:
        while not offline_account_queue.empty():
            try:
                offline_account_queue.get(block=False)
            except queue.Empty: break
    with loaded_offline_emails_lock:
        loaded_offline_emails.clear()
    print("✅ Offline 账户队列和已加载邮箱记录已重置")
