# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
FLASK_HOST = "0.0.0.0"  # 备注：阿里云服务器需保持0.0.0.0，允许外部访问
FLASK_PORT = 5000       # 备注：如需修改端口，同步修改项目A和项目C的对应配置
FLASK_DEBUG = False

# 飞书接口核心配置（原有内容不变）
FEISHU_APP_ID = "cli_a9f11298ecb85bd7"
FEISHU_APP_SECRET = "qn7gh7ggMCLcpXEfxzONheu1wHZysMkW"
FEISHU_RANGE_STR = "A:N"  # 原有订单表格范围

# ---------------- 新增：未认证账户表格配置 ----------------
# 固定未认证账户表格列表（sheetid + spreadsheetToken）
FEISHU_FIXED_SHEETS = [
    {"sheet_id": "3eb130", "spreadsheet_token": "ZmTWwo0VHiOXakk5M3PcEOKonzb"},
    {"sheet_id": "253571", "spreadsheet_token": "TX74w2JYPia8ZJk8Lmdc279vn0g"},
    {"sheet_id": "ccdb49", "spreadsheet_token": "KVeBwDXLKi4eSFkisRHcWCS2nJc"},
    {"sheet_id": "ab86d4", "spreadsheet_token": "ZqHDwTs29iLeZbkegq5cd83Snlc"}
]

# 未认证账户表格读取范围（对应你的表格A-H列）
FEISHU_ACCOUNT_RANGE_STR = "A:H"