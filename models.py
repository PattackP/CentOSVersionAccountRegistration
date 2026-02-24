# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
#models.py
class Order:
    """订单类（对应飞书表格A-N列，包含新增的sheetid、spreadsheetToken）"""
    def __init__(self, row_num, sheetid, spreadsheet_token, order_id, link, sku_color, sku_size,
                 first_name, last_name, address, phone, city, state, zip_code, window_num):
        # 原有核心字段逻辑不变，仅新增2个列字段
        self.row_num = row_num          # A列：行号
        self.sheetid = sheetid          # B列：新增 - sheetid
        self.spreadsheet_token = spreadsheet_token  # C列：新增 - spreadsheetToken
        self.order_id = order_id        # D列：订单ID
        self.link = link                # E列：纯净URL链接
        self.sku_color = sku_color      # F列：SKU-颜色
        self.sku_size = sku_size        # F列：SKU-尺寸
        self.first_name = first_name    # G列：FirstName
        self.last_name = last_name      # H列：LastName
        self.address = address          # I列：详细地址
        self.phone = phone              # J列：联系电话
        self.city = city                # K列：城市
        self.state = state              # L列：州
        self.zip_code = zip_code        # M列：邮编
        self.window_num = window_num    # N列：确认订单比特窗口号

    def to_dict(self):
        """转换为字典，方便JSON返回（SKU嵌套格式，包含新增列）"""
        return {
            'row_num': self.row_num,
            'sheetid': self.sheetid,      # 新增 - 保留原有嵌套核心逻辑
            'spreadsheet_token': self.spreadsheet_token,  # 新增
            'order_id': self.order_id,
            'link': self.link,
            # 原有核心逻辑：SKU嵌套字典不变
            'sku': {
                'sku-color': self.sku_color,
                'sku-size': self.sku_size
            },
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'phone': self.phone,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'window_num': self.window_num
        }

# ---------------- 新增：未认证账户模型类 ----------------
class Account:
    """未认证账户类（对应飞书表格A-H列，邮箱账号唯一）"""
    def __init__(self, row_num, sheetid, spreadsheet_token, email_account, email_password, env, proxy_address, window_id):
        self.row_num = row_num          # A列：行号
        self.sheetid = sheetid          # B列：sheetid
        self.spreadsheet_token = spreadsheet_token  # C列：spreadsheetToken
        self.email_account = email_account  # D列：邮箱账号（唯一标识）
        self.email_password = email_password  # E列：邮箱密码
        self.env = env                  # F列：环境
        self.proxy_address = proxy_address  # G列：代理地址
        self.window_id = window_id      # H列：窗口id

    def to_dict(self):
        """转换为字典，方便JSON返回"""
        return {
            'row_num': self.row_num,
            'sheetid': self.sheetid,
            'spreadsheet_token': self.spreadsheet_token,
            'email_account': self.email_account,
            'email_password': self.email_password,
            'env': self.env,
            'proxy_address': self.proxy_address,
            'window_id': self.window_id
        }