# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
#app.py
from flask import Flask
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from routes import register_routes
from token_manager import start_token_auto_refresh
from screenshot_manager import start_cleanup_thread
import datetime  # 新增：用于接口返回服务器时间

# 1. 创建Flask应用实例
app = Flask(__name__)

# 2. 注册所有路由（包含订单接口和新增的账户接口）
register_routes(app)

# 3. 启动飞书Token自动刷新线程
start_token_auto_refresh()

# 4. 启动截图缓存自动清理线程
start_cleanup_thread()

# 5. 启动服务器
if __name__ == '__main__':
    print("=" * 50)
    print("订单队列服务器（支持指定表格加载版 + 未认证账户版）启动")
    print(f"本地访问: http://127.0.0.1:{FLASK_PORT}")
    print("可用接口:")
    
    print("  [Authorized Accounts]")
    print("  GET  /load_authorized_accounts       - 加载已认证账户（J='该号是0.99'）")
    print("  GET  /get_authorized_account         - 获取一个已认证账户")
    print("  GET  /get_authorized_account_status  - 查看Authorized队列状态")
    print("  GET  /load_single_authorized_account - 手动加载指定账户")
    print("  GET  /reset_authorized_accounts      - 重置Authorized队列")

    print("\n  [Unauthorized Accounts]")
    print("  GET  /load_unauthorized_accounts     - 加载所有未创建账户到队列")
    print("  GET  /load_unauthorized_accounts_from - 加载指定表格未创建账户（传参：sheetid & spreadsheetToken）")
    print("  GET  /get_unauthorized_account       - 获取一个未创建账户的数据")
    print("  GET  /get_unauthorized_account_status - 查看未登录账户的队列状态")
    print("  GET  /update_process_tracing_column  - 更新流程追踪（J列）")
    print("  GET  /reset_unauthorized_accounts    - 重置Unauthorized队列")

    print("\n  [Offline Accounts]")
    print("  GET  /load_offline_accounts          - 加载所有离线账户（J列='使用过程中被弹出'）")
    print("  GET  /load_offline_accounts_from     - 加载指定表格离线账户（传参：sheetid & spreadsheetToken）")
    print("  GET  /get_offline_account            - 获取一个离线账户")
    print("  GET  /get_offline_account_status     - 查看离线账户队列状态")
    print("  GET  /reset_offline_accounts         - 重置Offline队列")

    print("\n  [Orders]")
    print("  GET  /load_order_from      - 加载指定表格订单（传参：sheetid & spreadsheetToken）")
    print("  GET  /get_order            - 获取一个订单")
    print("  GET  /order_status         - 查看订单队列状态")
    print("  GET  /update_order_window_num - 更新订单窗口号（N列）")

    print("\n  [Screenshots]")
    print("  POST /upload_screenshot           - 上传截图")
    print("  GET  /get_all_latest_screenshots  - 获取所有截图")
    print("  GET  /get_screenshot_list         - 获取终端ID列表（分批获取优化）")
    print("  GET  /get_screenshot_by_id        - 获取指定终端截图（传参：terminal_id）")
    print("  GET  /get_screenshot_cache_status - 查看缓存状态（终端数/内存占用）")
    print("  GET  /clear_screenshot_cache      - 清空截图缓存")
    print("=" * 50)

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)