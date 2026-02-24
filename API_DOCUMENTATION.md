# API 接口文档 (v2.0)

本文档按照业务操作流程（先加载数据 -> 再获取数据 -> 查询状态 -> 重置/维护）的顺序编写。
所有 JSON 返回值均包含完整字段，便于开发调试和校验。

---

## 1. 认证账户相关 (Authorized Accounts)
**定义**：J列为 "该号是0.99" 的账户。

### 1.1 加载数据 (Load)
**接口**: `GET /load_authorized_accounts`
**描述**: 扫描配置文件中定义的飞书表格，将符合条件（J列="该号是0.99"）的账户加载到内存队列。
**响应示例**:
```json
{
    "success": true,
    "message": "已加载 12 个 Authorized 账户到队列"
}
```

### 1.2 获取单个账户 (Get)
**接口**: `GET /get_authorized_account`
**描述**: 从队列中取出一个已认证账户（FIFO），取出后队列长度减1。
**响应示例 (成功)**:
```json
{
    "success": true,
    "account": {
        "row_num": "2",
        "sheetid": "3eb130",
        "spreadsheet_token": "ZmTWwo0VHiOXakk5M3PcEOKonzb",
        "email_account": "test_auth@example.com",
        "email_password": "password123",
        "env": "production",
        "proxy_address": "192.168.1.100:8888",
        "window_id": "1"
    },
    "remaining_accounts": 11
}
```
**响应示例 (队列为空)**:
```json
{
    "success": false,
    "message": "已认证账户队列已空",
    "remaining_accounts": 0
}
```

### 1.3 查询状态 (Status)
**接口**: `GET /get_authorized_account_status`
**描述**: 查看当前 Authorized 队列中剩余的账户数量。
**响应示例**:
```json
{
    "success": true,
    "queue_size": 11,
    "is_empty": false
}
```

### 1.4 手动加载单个账户 (Manual Load)
**接口**: `GET /load_single_authorized_account?sheet_id=...&token=...&row=...`
**参数**:
- `sheet_id`: 表格 sheetID
- `token`: 表格 spreadsheetToken
- `row`: 行号
**描述**: 强制加载指定行的数据到 Authorized 队列（即使 J 列不是 "该号是0.99" 也可以加载，用于测试）。
**响应示例**:
```json
{
    "success": true,
    "message": "账户 test_auth@example.com 加载成功"
}
```

### 1.5 重置队列 (Reset)
**接口**: `GET /reset_authorized_accounts`
**描述**: 清空 Authorized 队列和已加载的邮箱去重记录。
**响应示例**:
```json
{
    "success": true,
    "message": "Authorized账户队列和已加载邮箱记录已重置"
}
```

---

## 2. 未认证账户相关 (Unauthorized Accounts)
**定义**：H列（window_id）不为空，且 J列 **不是** "该号是0.99" 的账户。

### 2.1 加载数据 (Load)
**接口**: `GET /load_unauthorized_accounts`
**描述**: 扫描飞书表格，将未认证账户加载到内存队列。
**响应示例**:
```json
{
    "success": true,
    "message": "已加载 50 个 Unauthorized 账户到队列"
}
```

### 2.2 获取单个账户 (Get)
**接口**: `GET /get_unauthorized_account`
**描述**: 从队列中取出一个未认证账户（FIFO）。
**响应示例 (成功)**:
```json
{
    "success": true,
    "account": {
        "row_num": "5",
        "sheetid": "253571",
        "spreadsheet_token": "TX74w2JYPia8ZJk8Lmdc279vn0g",
        "email_account": "new_user@example.com",
        "email_password": "password456",
        "env": "production",
        "proxy_address": "192.168.1.101:8888",
        "window_id": "2"
    },
    "remaining_accounts": 49
}
```

### 2.3 查询状态 (Status)
**接口**: `GET /get_unauthorized_account_status`
**描述**: 查看当前 Unauthorized 队列剩余数量。
**响应示例**:
```json
{
    "success": true,
    "queue_size": 49,
    "is_empty": false
}
```

### 2.4 更新流程追踪 (Update J Column)
**接口**: `GET /update_process_tracing_column?sheetid=...&spreadsheettoken=...&row_num=...&content=...`
**描述**: 更新表格 J 列（流程追踪列）的内容。
**响应示例**:
```json
{
    "success": true,
    "message": "流程追踪列内容更新成功",
    "target_cell": "3eb130!J5",
    "written_content": "注册成功"
}
```

### 2.5 重置队列 (Reset)
**接口**: `GET /reset_unauthorized_accounts`
**描述**: 清空 Unauthorized 队列和去重记录。
**响应示例**:
```json
{
    "success": true,
    "message": "Unauthorized账户队列和已加载邮箱记录已重置"
}
```

---

## 3. 订单相关 (Orders)

### 3.1 加载指定表格 (Load)
**接口**: `GET /load_order_from?sheetid=...&spreadsheetToken=...`
**描述**: 清空当前订单队列，并从指定表格加载订单数据。
**响应示例**:
```json
{
    "success": true,
    "message": "成功从指定表格加载 100 条订单"
}
```

### 3.2 获取单个订单 (Get)
**接口**: `GET /get_order`
**描述**: 获取一个待处理订单。
**响应示例**:
```json
{
    "success": true,
    "order": {
        "row_num": "10",
        "sheetid": "ccdb49",
        "spreadsheet_token": "KVeBwDXLKi4eSFkisRHcWCS2nJc",
        "order_id": "114-1234567-8901234",
        "link": "https://www.amazon.com/dp/B08...",
        "sku": {
            "sku-color": "Black",
            "sku-size": "L"
        },
        "first_name": "John",
        "last_name": "Doe",
        "address": "123 Main St",
        "phone": "1234567890",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "window_num": ""
    },
    "remaining": 99
}
```

### 3.3 查询状态 (Status)
**接口**: `GET /order_status`
**响应示例**:
```json
{
    "success": true,
    "queue_size": 99,
    "is_empty": false
}
```

### 3.4 更新订单窗口号 (Update N Column)
**接口**: `GET /update_order_window_num?sheetid=...&spreadsheettoken=...&row_num=...&window_num=...`
**描述**: 更新订单表格 N 列（确认订单比特窗口号）的内容。
**参数**:
- `sheetid`: 飞书子表格 ID (从 `get_order` 返回值获取)
- `spreadsheettoken`: 飞书文档 Token (从 `get_order` 返回值获取)
- `row_num`: 行号 (从 `get_order` 返回值获取)
- `window_num`: 窗口号 (要写入的内容)
**响应示例**:
```json
{
    "success": true,
    "message": "订单窗口号更新成功",
    "target_cell": "e776cc!N2",
    "written_content": "Window-05"
}
```

---

## 4. 截图缓存相关 (Screenshots)

### 4.1 上传截图 (Upload)
**接口**: `POST /upload_screenshot`
**Content-Type**: `application/json`
**Body**:
```json
{
    "terminal_id": "VM-001",
    "screenshot_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
    "update_time": "2023-10-27 10:00:00"
}
```
**响应示例**:
```json
{
    "success": true,
    "message": "截图缓存更新成功",
    "terminal_id": "VM-001"
}
```

### 4.2 获取所有截图 (Get All)
**接口**: `GET /get_all_latest_screenshots`
**响应示例**:
```json
{
    "success": true,
    "screenshots": [
        {
            "terminal_id": "VM-001",
            "screenshot_base64": "...",
            "update_time": "2023-10-27 10:00:00"
        },
        {
            "terminal_id": "VM-002",
            "screenshot_base64": "...",
            "update_time": "2023-10-27 10:05:00"
        }
    ],
    "count": 2
}
```

### 4.3 清空缓存 (Clear)
**接口**: `GET /clear_screenshot_cache`
**响应示例**:
```json
{
    "success": true,
    "message": "截图缓存已清空",
    "cleared_count": 2
}
```
