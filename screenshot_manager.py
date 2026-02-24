# -*- coding: utf-8 -*-
from threading import Lock, Thread
from datetime import datetime, timedelta
import time

# ---------------- 截图缓存配置 ----------------
CACHE_EXPIRE_MINUTES = 30
MAX_CACHE_SIZE = 200
CLEANUP_INTERVAL_SECONDS = 300

# ---------------- 截图缓存管理 ----------------
SCREENSHOT_CACHE = {}
SCREENSHOT_CACHE_LOCK = Lock()

_cleanup_thread = None
_cleanup_running = False

def update_screenshot_cache(terminal_id, screenshot_base64, update_time):
    with SCREENSHOT_CACHE_LOCK:
        op_type = "首次添加" if terminal_id not in SCREENSHOT_CACHE else "覆盖更新"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] ℹ️  截图缓存{op_type} - 终端ID：{terminal_id}，当前缓存终端总数：{len(SCREENSHOT_CACHE)+(1 if op_type=='首次添加' else 0)}")
        SCREENSHOT_CACHE[terminal_id] = {
            "screenshot_base64": screenshot_base64,
            "update_time": update_time,
            "terminal_id": terminal_id,
            "cached_at": datetime.now()
        }

def get_all_screenshot_cache():
    with SCREENSHOT_CACHE_LOCK:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] ℹ️  读取截图缓存 - 当前缓存终端总数：{len(SCREENSHOT_CACHE)}")
        return list(SCREENSHOT_CACHE.values()).copy()

def get_screenshot_list():
    with SCREENSHOT_CACHE_LOCK:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] ℹ️  读取终端列表 - 当前缓存终端总数：{len(SCREENSHOT_CACHE)}")
        return [
            {
                "terminal_id": data["terminal_id"],
                "update_time": data["update_time"]
            }
            for data in SCREENSHOT_CACHE.values()
        ]

def get_screenshot_by_id(terminal_id):
    with SCREENSHOT_CACHE_LOCK:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if terminal_id in SCREENSHOT_CACHE:
            print(f"[{current_time}] ℹ️  读取单个截图 - 终端ID：{terminal_id}")
            return SCREENSHOT_CACHE[terminal_id].copy()
        print(f"[{current_time}] ⚠️  截图不存在 - 终端ID：{terminal_id}")
        return None

def clear_screenshot_cache():
    with SCREENSHOT_CACHE_LOCK:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cache_count = len(SCREENSHOT_CACHE)
        SCREENSHOT_CACHE.clear()
        print(f"[{current_time}] ℹ️  截图缓存已清空 - 共清除{cache_count}个终端的截图数据")
        return cache_count

def get_cache_status():
    """获取缓存状态信息"""
    with SCREENSHOT_CACHE_LOCK:
        total_size = 0
        for data in SCREENSHOT_CACHE.values():
            if data.get("screenshot_base64"):
                total_size += len(data["screenshot_base64"])
        
        return {
            "terminal_count": len(SCREENSHOT_CACHE),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "max_cache_size": MAX_CACHE_SIZE,
            "expire_minutes": CACHE_EXPIRE_MINUTES
        }

def _cleanup_expired_cache():
    """清理过期的缓存"""
    with SCREENSHOT_CACHE_LOCK:
        current_time = datetime.now()
        expire_threshold = current_time - timedelta(minutes=CACHE_EXPIRE_MINUTES)
        
        expired_terminals = [
            terminal_id for terminal_id, data in SCREENSHOT_CACHE.items()
            if data.get("cached_at") and data["cached_at"] < expire_threshold
        ]
        
        for terminal_id in expired_terminals:
            del SCREENSHOT_CACHE[terminal_id]
        
        if expired_terminals:
            print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 🧹 自动清理过期截图 - 共清除{len(expired_terminals)}个终端")
        
        return len(expired_terminals)

def _cleanup_oldest_cache():
    """当缓存超过最大限制时，清理最旧的数据"""
    with SCREENSHOT_CACHE_LOCK:
        if len(SCREENSHOT_CACHE) <= MAX_CACHE_SIZE:
            return 0
        
        sorted_items = sorted(
            SCREENSHOT_CACHE.items(),
            key=lambda x: x[1].get("cached_at", datetime.min)
        )
        
        remove_count = len(SCREENSHOT_CACHE) - MAX_CACHE_SIZE
        for i in range(remove_count):
            terminal_id = sorted_items[i][0]
            del SCREENSHOT_CACHE[terminal_id]
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] 🧹 缓存超限清理 - 清除最旧的{remove_count}个终端截图")
        
        return remove_count

def _cleanup_worker():
    """后台清理线程"""
    global _cleanup_running
    
    while _cleanup_running:
        try:
            _cleanup_expired_cache()
            _cleanup_oldest_cache()
        except Exception as e:
            print(f"[清理线程] 异常: {e}")
        
        time.sleep(CLEANUP_INTERVAL_SECONDS)

def start_cleanup_thread():
    """启动后台清理线程"""
    global _cleanup_thread, _cleanup_running
    
    if _cleanup_thread is not None and _cleanup_thread.is_alive():
        print("⚠️  截图清理线程已在运行")
        return
    
    _cleanup_running = True
    _cleanup_thread = Thread(target=_cleanup_worker, daemon=True)
    _cleanup_thread.start()
    print(f"✅ 截图自动清理线程已启动 - 过期时间:{CACHE_EXPIRE_MINUTES}分钟, 最大缓存:{MAX_CACHE_SIZE}个终端, 检查间隔:{CLEANUP_INTERVAL_SECONDS}秒")

def stop_cleanup_thread():
    """停止后台清理线程"""
    global _cleanup_running
    _cleanup_running = False
    print("ℹ️  截图清理线程已停止")
