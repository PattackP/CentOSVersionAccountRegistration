# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
#token_manager.py
import requests
import time
import threading
from datetime import datetime, timedelta
from config import FEISHU_APP_ID, FEISHU_APP_SECRET

# 飞书Token接口地址
FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"

# 全局缓存（存储有效 Token 和过期信息）
TOKEN_CACHE = {
    "app_access_token": None,
    "tenant_access_token": None,
    "expire_time": None,  # Token 过期时间（datetime 类型）
    "expire_seconds": 0   # Token 有效期（秒）
}

# 线程锁，避免并发刷新 Token 导致冲突
token_lock = threading.Lock()

def _fetch_feishu_token():
    """
    私有方法：直接调用飞书接口获取 Token（不做缓存，仅负责网络请求）
    返回：成功返回 Token 字典，失败返回 None
    """
    try:
        # 构建请求头和请求体
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET
        }

        # 发送 POST 请求
        response = requests.post(FEISHU_TOKEN_URL, json=data, headers=headers, timeout=30)
        response.raise_for_status()  # 抛出 HTTP 错误（如 400、403 等）
        result = response.json()

        # 检查响应码是否成功
        if result.get("code") == 0:
            return {
                "app_access_token": result.get("app_access_token"),
                "tenant_access_token": result.get("tenant_access_token"),
                "expire_seconds": result.get("expire", 7200),  # 默认 2 小时
                "fetch_time": datetime.now()  # 记录获取时间
            }
        else:
            print(f"获取 Token 失败：飞书返回错误 - {result.get('msg')}（错误码：{result.get('code')}）")
            return None
    except Exception as e:
        print(f"获取 Token 失败：网络/解析错误 - {str(e)}")
        return None

def refresh_feishu_token(force_refresh=False):
    """
    公开方法：刷新 Token（支持强制刷新）
    :param force_refresh: 是否强制刷新（即使 Token 有效期大于 30 分钟）
    :return: 成功返回 True，失败返回 False
    """
    global TOKEN_CACHE

    with token_lock:  # 加锁，避免多线程并发刷新
        # 1. 检查是否需要刷新（非强制刷新时）
        if not force_refresh:
            current_time = datetime.now()
            expire_time = TOKEN_CACHE.get("expire_time")

            # 如果 Token 存在且有效期大于 30 分钟，无需刷新（返回 True，使用原有 Token）
            if expire_time and (expire_time - current_time) > timedelta(minutes=30):
                return True

        # 2. 调用飞书接口获取新 Token
        token_data = _fetch_feishu_token()
        if not token_data:
            return False

        # 3. 更新全局缓存
        fetch_time = token_data.get("fetch_time")
        expire_seconds = token_data.get("expire_seconds")
        TOKEN_CACHE.update({
            "app_access_token": token_data.get("app_access_token"),
            "tenant_access_token": token_data.get("tenant_access_token"),
            "expire_time": fetch_time + timedelta(seconds=expire_seconds),
            "expire_seconds": expire_seconds
        })

        print(f"Token 刷新成功！有效期至：{TOKEN_CACHE['expire_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        return True

def get_valid_feishu_token(token_type="app_access_token"):
    """
    公开方法：获取有效 Token（每次请求飞书接口前调用此方法）
    :param token_type: Token 类型（"app_access_token" 或 "tenant_access_token"）
    :return: 有效 Token 字符串（失败返回 None）
    """
    # 1. 首次调用：初始化 Token
    if not TOKEN_CACHE.get(token_type):
        if not refresh_feishu_token():
            return None

    # 2. 检查 Token 是否过期（提前 30 分钟刷新）
    refresh_feishu_token(force_refresh=False)

    # 3. 返回有效 Token
    return TOKEN_CACHE.get(token_type)

def _schedule_token_refresh():
    """
    私有方法：定时刷新 Token（循环执行）
    刷新间隔：1 小时 50 分钟（小于 2 小时有效期，避免 Token 过期）
    """
    while True:
        # 等待 1 小时 50 分钟（110 * 60 秒）
        time.sleep(110 * 60)

        # 执行刷新
        refresh_feishu_token(force_refresh=False)

def start_token_auto_refresh():
    """
    公开方法：启动 Token 自动刷新线程（后台运行，不阻塞主程序）
    """
    # 启动后台线程，执行定时刷新
    refresh_thread = threading.Thread(
        target=_schedule_token_refresh,
        daemon=True,  # 守护线程：主程序退出时，线程自动终止
        name="FeishuTokenRefreshThread"
    )
    refresh_thread.start()
    print("Token 自动刷新线程已启动（每 1 小时 50 分钟刷新一次）")