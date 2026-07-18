# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
#app.py
from flask import Flask
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from routes import register_routes
from token_manager import start_token_auto_refresh

# 1. 创建Flask应用实例
app = Flask(__name__)

# 2. 注册所有路由
register_routes(app)

# 3. 启动飞书Token自动刷新线程
start_token_auto_refresh()

# 4. 启动服务器
if __name__ == '__main__':
    print("=" * 50)
    print("飞书表格读写服务器启动")
    print(f"本地访问: http://127.0.0.1:{FLASK_PORT}")
    print("可用接口:")

    print("  [飞书表格读取]")
    print("  GET  /read_sheet_data           - 读取表格数据（传参：sheetid、spreadsheettoken、range）")

    print("\n  [飞书表格写入]")
    print("  GET  /update_cell               - 更新指定单元格（传参：sheetid、spreadsheettoken、cell_range、content）")
    print("  GET  /update_process_tracing_column - 更新流程追踪J列（传参：sheetid、spreadsheettoken、row_num、content）")
    print("  GET  /update_order_window_num   - 更新订单窗口号N列（传参：sheetid、spreadsheettoken、row_num、window_num）")

    print("\n  [手机号队列]")
    print("  GET  /load_phone_queue          - 加载手机号队列（从表格253571读取）")
    print("  GET  /get_phone_data            - 从队列取出一条数据（FIFO）")
    print("  GET  /put_back_phone_data       - 放回未消费成功的数据（传参：row_num、sheetid、spreadsheettoken、phone_number、sms_url）")
    print("  GET  /update_window_name        - 在F列写入窗口名称（传参：row_num、sheetid、spreadsheettoken、window_name）")
    print("  GET  /phone_queue_status        - 查看队列状态")
    print("=" * 50)

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
