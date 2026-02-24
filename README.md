<div align="center">

# 🚀 CentOS 订单队列服务器

**基于 Flask 的订单队列管理服务 | 飞书表格深度集成**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0.3-green?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Internal-red)]()
[![API](https://img.shields.io/badge/API-15%20Endpoints-orange)]()

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [API文档](#-api-文档) • [部署](#-部署)

</div>

---

## 📖 目录

- [功能特性](#-功能特性)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [API 文档](#-api-文档)
  - [已认证账户接口](#一已认证账户接口-authorized)
  - [未认证账户接口](#二未认证账户接口-unauthorized)
  - [订单接口](#三订单接口-orders)
  - [截图接口](#四截图接口-screenshots)
- [数据模型](#-数据模型)
- [配置说明](#️-配置说明)
- [业务逻辑](#-业务逻辑)
- [部署指南](#-部署)

---

## ✨ 功能特性

<table>
<tr>
<td width="50%">

### 📦 订单队列管理
- 从飞书表格加载订单到内存队列
- 支持多客户端并发获取
- 自动过滤已处理订单
- 随机生成美式姓名电话

</td>
<td width="50%">

### 👤 账户队列管理
- **Authorized**: 已认证账户队列
- **Unauthorized**: 未认证账户队列
- 邮箱级别去重机制
- 支持手动加载指定账户

</td>
</tr>
<tr>
<td width="50%">

### 📸 终端截图同步
- 多终端截图上传
- 内存缓存最新截图
- 客户端轮询获取
- 支持缓存清理

</td>
<td width="50%">

### 🔗 飞书 API 集成
- 自动 Token 刷新机制
- 表格数据读取/写入
- 流程追踪更新
- 多表格支持

</td>
</tr>
</table>

---

## 📁 项目结构

```
📦 CentOSVersionComfirmOrder/
├── 📄 app.py                 # Flask 应用入口
├── 📄 config.py              # 配置文件
├── 📄 routes.py              # 路由定义
├── 📄 models.py              # 数据模型
├── 📄 order_manager.py       # 订单队列管理
├── 📄 account_manager.py     # 账户队列管理
├── 📄 screenshot_manager.py  # 截图缓存管理
├── 📄 feishu_api.py          # 飞书 API 封装
├── 📄 token_manager.py       # Token 自动刷新
├── 📄 requirements.txt       # Python 依赖
└── 📄 README.md              # 项目文档
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置飞书凭证

编辑 `config.py`：

```python
FEISHU_APP_ID = "your_app_id"
FEISHU_APP_SECRET = "your_app_secret"
```

### 启动服务

```bash
python app.py
```

<div align="center">

```
==================================================
订单队列服务器（支持指定表格加载版 + 未认证账户版）启动
本地访问: http://127.0.0.1:5000
==================================================
```

</div>

---

## 📚 API 文档

### 一、已认证账户接口

> 用于管理 J 列标记为 `"该号是0.99"` 的账户

<table>
<tr>
<th width="25%">接口</th>
<th width="15%">方法</th>
<th width="60%">描述</th>
</tr>
<tr>
<td><code>/load_authorized_accounts</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>加载所有已认证账户到队列</td>
</tr>
<tr>
<td><code>/get_authorized_account</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>获取一个已认证账户</td>
</tr>
<tr>
<td><code>/get_authorized_account_status</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>查看队列状态</td>
</tr>
<tr>
<td><code>/load_single_authorized_account</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>手动加载指定账户</td>
</tr>
<tr>
<td><code>/reset_authorized_accounts</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>重置队列</td>
</tr>
</table>

<details>
<summary><b>📋 接口详情</b></summary>

#### 1.1 加载已认证账户

```http
GET /load_authorized_accounts
```

**响应示例：**

```json
{
    "success": true,
    "message": "已认证账户表格加载完成",
    "total_loaded_accounts": 50,
    "current_account_queue_size": 50
}
```

---

#### 1.2 获取一个已认证账户

```http
GET /get_authorized_account
```

**响应示例：**

```json
{
    "success": true,
    "account": {
        "row_num": "2",
        "sheetid": "3eb130",
        "spreadsheet_token": "ZmTWwo0VHiOXakk5M3PcEOKonzb",
        "email_account": "user@example.com",
        "email_password": "password123",
        "env": "production",
        "proxy_address": "192.168.1.1:8080",
        "window_id": "window_001"
    },
    "remaining_accounts": 49
}
```

---

#### 1.3 查看队列状态

```http
GET /get_authorized_account_status
```

**响应示例：**

```json
{
    "success": true,
    "queue_size": 50,
    "is_empty": false
}
```

---

#### 1.4 手动加载指定账户

```http
GET /load_single_authorized_account?sheetid=3eb130&spreadsheetToken=ZmTWwo0VHiOXakk5M3PcEOKonzb&row_num=5
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `sheetid` | string | ✅ | 飞书表格 sheet ID |
| `spreadsheetToken` | string | ✅ | 飞书表格 token |
| `row_num` | string | ✅ | 要加载的行号 |

---

#### 1.5 重置队列

```http
GET /reset_authorized_accounts
```

**响应示例：**

```json
{
    "success": true,
    "message": "Authorized账户队列和已加载邮箱记录已重置"
}
```

</details>

---

### 二、未认证账户接口

> 用于管理 J 列**不是** `"该号是0.99"` 的账户

<table>
<tr>
<th width="25%">接口</th>
<th width="15%">方法</th>
<th width="60%">描述</th>
</tr>
<tr>
<td><code>/load_unauthorized_accounts</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>加载所有未认证账户到队列</td>
</tr>
<tr>
<td><code>/get_unauthorized_account</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>获取一个未认证账户</td>
</tr>
<tr>
<td><code>/get_unauthorized_account_status</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>查看队列状态</td>
</tr>
<tr>
<td><code>/update_process_tracing_column</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>更新流程追踪列（J列）</td>
</tr>
<tr>
<td><code>/reset_unauthorized_accounts</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>重置队列</td>
</tr>
</table>

<details>
<summary><b>📋 接口详情</b></summary>

#### 2.1 加载未认证账户

```http
GET /load_unauthorized_accounts
```

**响应示例：**

```json
{
    "success": true,
    "message": "固定未认证账户表格加载完成",
    "total_loaded_accounts": 100,
    "current_account_queue_size": 100
}
```

---

#### 2.2 获取一个未认证账户

```http
GET /get_unauthorized_account
```

**响应示例：**

```json
{
    "success": true,
    "account": {
        "row_num": "3",
        "sheetid": "3eb130",
        "spreadsheet_token": "ZmTWwo0VHiOXakk5M3PcEOKonzb",
        "email_account": "newuser@example.com",
        "email_password": "pass456",
        "env": "development",
        "proxy_address": "10.0.0.1:3128",
        "window_id": "window_002"
    },
    "remaining_accounts": 99
}
```

---

#### 2.3 查看队列状态

```http
GET /get_unauthorized_account_status
```

---

#### 2.4 更新流程追踪列

```http
GET /update_process_tracing_column?sheetid=3eb130&spreadsheettoken=ZmTWwo0VHiOXakk5M3PcEOKonzb&row_num=2&content=已处理
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `sheetid` | string | ✅ | 飞书表格 sheet ID |
| `spreadsheettoken` | string | ✅ | 飞书表格 token |
| `row_num` | string | ✅ | 要更新的行号 |
| `content` | string | ✅ | 要写入的内容 |

**响应示例：**

```json
{
    "success": true,
    "message": "流程追踪列内容更新成功",
    "target_cell": "3eb130!J2:J2",
    "written_content": "已处理"
}
```

---

#### 2.5 重置队列

```http
GET /reset_unauthorized_accounts
```

</details>

---

### 三、订单接口

<table>
<tr>
<th width="25%">接口</th>
<th width="15%">方法</th>
<th width="60%">描述</th>
</tr>
<tr>
<td><code>/load_order_from</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>从指定表格加载订单</td>
</tr>
<tr>
<td><code>/get_order</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>获取一个订单</td>
</tr>
<tr>
<td><code>/order_status</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>查看订单队列状态</td>
</tr>
<tr>
<td><code>/update_order_window_num</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>更新订单窗口号（N列）</td>
</tr>
</table>

<details>
<summary><b>📋 接口详情</b></summary>

#### 3.1 加载指定表格订单

```http
GET /load_order_from?sheetid=e776cc&spreadsheetToken=YCDPwawH8imUcHklVR9cXbL5nlh
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `sheetid` | string | ✅ | 飞书表格 sheet ID |
| `spreadsheetToken` | string | ✅ | 飞书表格 token |

---

#### 3.2 获取一个订单

```http
GET /get_order
```

**响应示例：**

```json
{
    "success": true,
    "order": {
        "row_num": "2",
        "sheetid": "e776cc",
        "spreadsheet_token": "YCDPwawH8imUcHklVR9cXbL5nlh",
        "order_id": "ORD123456",
        "link": "https://example.com/product/123",
        "sku": {
            "sku-color": "Red",
            "sku-size": "M"
        },
        "first_name": "Emma",
        "last_name": "Smith",
        "address": "123 Main St",
        "phone": "5551234567",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "window_num": ""
    },
    "remaining": 149
}
```

---

#### 3.3 查看订单队列状态

```http
GET /order_status
```

---

#### 3.4 更新订单窗口号

```http
GET /update_order_window_num?sheetid=e776cc&spreadsheettoken=YCDPwawH8imUcHklVR9cXbL5nlh&row_num=2&window_num=W001
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `sheetid` | string | ✅ | 飞书表格 sheet ID |
| `spreadsheettoken` | string | ✅ | 飞书表格 token |
| `row_num` | string | ✅ | 要更新的行号 |
| `window_num` | string | ✅ | 窗口号内容 |

</details>

---

### 四、截图接口

<table>
<tr>
<th width="25%">接口</th>
<th width="15%">方法</th>
<th width="60%">描述</th>
</tr>
<tr>
<td><code>/upload_screenshot</code></td>
<td><img src="https://img.shields.io/badge/POST-blue" /></td>
<td>上传终端截图</td>
</tr>
<tr>
<td><code>/get_all_latest_screenshots</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>获取所有最新截图</td>
</tr>
<tr>
<td><code>/clear_screenshot_cache</code></td>
<td><img src="https://img.shields.io/badge/GET-green" /></td>
<td>清空截图缓存</td>
</tr>
</table>

<details>
<summary><b>📋 接口详情</b></summary>

#### 4.1 上传截图

```http
POST /upload_screenshot
Content-Type: application/json
```

**请求体：**

```json
{
    "terminal_id": "terminal_001",
    "screenshot_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "update_time": "2024-01-15 10:30:00"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `terminal_id` | string | ✅ | 终端唯一标识 |
| `screenshot_base64` | string | ✅ | 截图的 Base64 编码 |
| `update_time` | string | ✅ | 截图更新时间 |

---

#### 4.2 获取所有最新截图

```http
GET /get_all_latest_screenshots
```

**响应示例：**

```json
{
    "success": true,
    "screenshot_count": 3,
    "screenshots": [
        {
            "terminal_id": "terminal_001",
            "screenshot_base64": "iVBORw0KGgo...",
            "update_time": "2024-01-15 10:30:00"
        }
    ],
    "server_time": "2024-01-15 10:32:00"
}
```

---

#### 4.3 清空截图缓存

```http
GET /clear_screenshot_cache
```

</details>

---

## 🗃️ 数据模型

### Order 订单模型

| 字段 | 列 | 类型 | 说明 |
|:-----|:--:|:----:|:-----|
| `row_num` | A | string | 行号 |
| `sheetid` | B | string | 飞书表格 sheet ID |
| `spreadsheet_token` | C | string | 飞书表格 token |
| `order_id` | D | string | 订单 ID |
| `link` | E | string | 商品链接 URL |
| `sku_color` | F | string | SKU 颜色 |
| `sku_size` | F | string | SKU 尺寸 |
| `first_name` | G | string | 名 |
| `last_name` | H | string | 姓 |
| `address` | I | string | 详细地址 |
| `phone` | J | string | 联系电话 |
| `city` | K | string | 城市 |
| `state` | L | string | 州 |
| `zip_code` | M | string | 邮编 |
| `window_num` | N | string | 窗口号 |

### Account 账户模型

| 字段 | 列 | 类型 | 说明 |
|:-----|:--:|:----:|:-----|
| `row_num` | A | string | 行号 |
| `sheetid` | B | string | 飞书表格 sheet ID |
| `spreadsheet_token` | C | string | 飞书表格 token |
| `email_account` | D | string | 邮箱账号（唯一标识） |
| `email_password` | E | string | 邮箱密码 |
| `env` | F | string | 环境 |
| `proxy_address` | G | string | 代理地址 |
| `window_id` | H | string | 窗口 ID |

---

## ⚙️ 配置说明

<details>
<summary><b>🔧 config.py 配置项</b></summary>

```python
# 服务配置
FLASK_HOST = "0.0.0.0"    # 监听地址
FLASK_PORT = 5000          # 服务端口
FLASK_DEBUG = False        # 调试模式

# 飞书凭证
FEISHU_APP_ID = "xxx"      # 飞书应用 ID
FEISHU_APP_SECRET = "xxx"  # 飞书应用密钥

# 表格范围
FEISHU_RANGE_STR = "A:N"   # 订单表格范围
FEISHU_ACCOUNT_RANGE_STR = "A:H"  # 账户表格范围

# 固定账户表格列表
FEISHU_FIXED_SHEETS = [
    {"sheet_id": "3eb130", "spreadsheet_token": "xxx"},
    {"sheet_id": "253571", "spreadsheet_token": "xxx"},
    # ...
]
```

</details>

---

## 🧠 业务逻辑

### 订单加载流程

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   飞书表格读取   │ ──▶│  过滤 N列为空   │ ──▶│  每行复制5份   │
│   (A-N列数据)   │    │  (未处理订单)   │    │  加入队列      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
                                                      ▼
                                              ┌─────────────────┐
                                              │ 生成随机美式    │
                                              │ 姓名和电话号码  │
                                              └─────────────────┘
```

### 账户分类逻辑

| 队列类型 | 过滤条件 | 用途 |
|:---------|:---------|:-----|
| **Authorized** | J 列 = `"该号是0.99"` | 已认证账户，可直接使用 |
| **Unauthorized** | J 列 ≠ `"该号是0.99"` | 未认证账户，需要注册流程 |

### Token 自动刷新

```
┌────────────────────────────────────────────────────────────┐
│                    飞书 Token 管理流程                      │
├────────────────────────────────────────────────────────────┤
│  1. 后台线程每 30 分钟检查 Token 有效期                     │
│  2. 有效期 < 30 分钟时自动刷新                              │
│  3. 线程锁保证并发安全                                      │
│  4. 失败时自动重试                                          │
└────────────────────────────────────────────────────────────┘
```

---

## 🚢 部署

### 使用 Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Systemd 服务

<details>
<summary><b>📄 创建服务文件</b></summary>

```bash
sudo nano /etc/systemd/system/order-server.service
```

```ini
[Unit]
Description=Order Queue Server
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/CentOSVersionComfirmOrder
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**启动服务：**

```bash
sudo systemctl daemon-reload
sudo systemctl start order-server
sudo systemctl enable order-server
```

</details>

---

## ⚠️ 错误处理

所有接口返回统一格式：

| 状态码 | 说明 |
|:------:|:-----|
| `200` | 请求成功 |
| `400` | 参数缺失或格式错误 |
| `404` | 资源不存在（如队列为空） |
| `500` | 服务器内部错误 |

**错误响应格式：**

```json
{
    "success": false,
    "message": "错误描述信息"
}
```

---

## 📦 依赖版本

| 包名 | 版本 |
|:-----|:-----|
| Flask | 2.0.3 |
| requests | 2.27.1 |
| gunicorn | 21.2.0 |

---

<div align="center">

**Made with ❤️ for internal use**

</div>
