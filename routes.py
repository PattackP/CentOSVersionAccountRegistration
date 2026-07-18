# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
# routes.py
# 路由统一注册入口
from feishu_routes import register_feishu_routes
from phone_queue_routes import register_phone_queue_routes


def register_routes(app):
    """注册所有Flask路由"""
    # 飞书表格读写接口
    register_feishu_routes(app)
    # 手机号队列接口
    register_phone_queue_routes(app)
