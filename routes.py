# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
# routes.py
from datetime import datetime
import traceback
import sys
from flask import jsonify, request

# Import from new modular services
from order_manager import (
    get_order_queue_status,
    reinit_order_queue_from_feishu,
    get_order_and_remaining,
    load_order_from_specified_sheet
)
from account_manager import (
    load_all_authorized_accounts,
    load_all_unauthorized_accounts,
    load_unauthorized_accounts_from_sheet,
    load_all_offline_accounts,
    load_offline_accounts_from_sheet,
    get_account_queue_status,
    get_unauthorized_account,
    get_authorized_account,
    get_offline_account,
    get_authorized_queue_status,
    get_unauthorized_queue_status,
    get_offline_queue_status,
    load_single_authorized_account,
    reset_authorized_queue_and_emails,
    reset_unauthorized_queue_and_emails,
    reset_offline_queue_and_emails
)
from feishu_api import update_feishu_sheet_cell
from screenshot_manager import (
    update_screenshot_cache,
    get_all_screenshot_cache,
    clear_screenshot_cache,
    get_screenshot_list,
    get_screenshot_by_id,
    get_cache_status
)

def register_routes(app):
    """注册所有Flask路由（包含订单接口和账户接口）"""

    # ---------------- 原有订单接口 ----------------
    @app.route('/get_order', methods=['GET'])
    def get_order():
        try:
            order, remaining = get_order_and_remaining()
            if order:
                print(f"[API] get_order: Success, remaining={remaining}")
                return jsonify({
                    'success': True,
                    'order': order.to_dict(),
                    'remaining': remaining
                })
            else:
                print("[API] get_order: Queue empty")
                return jsonify({
                    'success': False,
                    'message': '订单队列已空',
                    'remaining': 0
                }), 404
        except Exception as e:
            print(f"[API] get_order Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/order_status', methods=['GET'])
    def order_status():
        try:
            status = get_order_queue_status()
            print(f"[API] order_status: size={status['queue_size']}")
            return jsonify({
                'success': True,
                'queue_size': status['queue_size'],
                'is_empty': status['is_empty']
            })
        except Exception as e:
            print(f"[API] order_status Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/load_order_from', methods=['GET'])
    def load_order_from():
        sheetid = request.args.get('sheetid')
        spreadsheetToken = request.args.get('spreadsheetToken')

        if not sheetid or not spreadsheetToken:
            return jsonify({
                'success': False,
                'message': '参数缺失，请同时提供sheetid和spreadsheetToken',
                'error_detail': 'URL格式示例：/load_order_from?sheetid=e776cc&spreadsheetToken=YCDPwawH8imUcHklVR9cXbL5nlh'
            }), 400

        try:
            load_result = load_order_from_specified_sheet(
                sheet_id=sheetid,
                spreadsheet_token=spreadsheetToken
            )
            if load_result:
                current_status = get_order_queue_status()
                return jsonify({
                    'success': True,
                    'message': '指定表格订单加载成功',
                    'target_sheetid': sheetid,
                    'current_queue_size': current_status['queue_size']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '指定表格订单加载失败，请查看服务端终端日志',
                    'target_sheetid': sheetid
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'加载过程出现异常：{str(e)}',
                'target_sheetid': sheetid
            }), 500

    @app.route('/reinit_order_queue', methods=['GET'])
    def reinit_order_queue():
        """重新初始化订单队列（传参模式，需提供sheetid和spreadsheetToken）"""
        sheetid = request.args.get('sheetid')
        spreadsheetToken = request.args.get('spreadsheetToken')

        if not sheetid or not spreadsheetToken:
            return jsonify({
                'success': False,
                'message': '参数缺失，请同时提供sheetid和spreadsheetToken',
                'error_detail': 'URL格式示例：/reinit_order_queue?sheetid=e776cc&spreadsheetToken=YCDPwawH8imUcHklVR9cXbL5nlh'
            }), 400

        try:
            result = reinit_order_queue_from_feishu(
                sheet_id=sheetid,
                spreadsheet_token=spreadsheetToken
            )
            if result:
                current_status = get_order_queue_status()
                return jsonify({
                    'success': True,
                    'message': '指定表格订单队列重新初始化成功',
                    'target_sheetid': sheetid,
                    'current_queue_size': current_status['queue_size']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '指定表格订单队列重新初始化失败，请查看服务端终端日志',
                    'target_sheetid': sheetid
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'重新初始化过程出现异常：{str(e)}',
                'target_sheetid': sheetid
            }), 500

    # ---------------- 新增：未认证账户接口 ----------------
    @app.route('/load_unauthorized_accounts', methods=['GET'])
    def load_unauthorized_accounts():
        """加载所有固定未认证账户数据到队列（RESTful风格，邮箱级去重）"""
        try:
            loaded_count = load_all_unauthorized_accounts()
            current_status = get_unauthorized_queue_status()
            return jsonify({
                'success': True,
                'message': '固定未认证账户表格加载完成',
                'total_loaded_accounts': loaded_count,
                'current_account_queue_size': current_status['queue_size']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'加载失败：{str(e)}'
            }), 500

    @app.route('/load_unauthorized_accounts_from', methods=['GET'])
    def load_unauthorized_accounts_from():
        """加载指定表格的未认证账户到队列"""
        sheetid = request.args.get('sheetid')
        spreadsheetToken = request.args.get('spreadsheetToken')

        if not sheetid or not spreadsheetToken:
            return jsonify({
                'success': False,
                'message': '参数缺失，请同时提供sheetid和spreadsheetToken',
                'error_detail': 'URL格式示例：/load_unauthorized_accounts_from?sheetid=3eb130&spreadsheetToken=xxx'
            }), 400

        try:
            loaded_count = load_unauthorized_accounts_from_sheet(sheetid, spreadsheetToken)
            current_status = get_unauthorized_queue_status()
            return jsonify({
                'success': True,
                'message': '指定表格未认证账户加载完成',
                'target_sheetid': sheetid,
                'total_loaded_accounts': loaded_count,
                'current_account_queue_size': current_status['queue_size']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'加载失败：{str(e)}',
                'target_sheetid': sheetid
            }), 500

    @app.route('/load_authorized_accounts', methods=['GET'])
    def load_authorized_accounts():
        """加载所有已认证账户数据到队列（J列=0.99）"""
        try:
            loaded_count = load_all_authorized_accounts()
            current_status = get_authorized_queue_status()
            return jsonify({
                'success': True,
                'message': '已认证账户表格加载完成',
                'total_loaded_accounts': loaded_count,
                'current_account_queue_size': current_status['queue_size']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'加载失败：{str(e)}'
            }), 500

    @app.route('/get_unauthorized_account', methods=['GET'])
    def get_unauthorized_account_api():
        """获取单个未认证账户（用于注册流程）"""
        try:
            print("[API] get_unauthorized_account: Request received")
            account = get_unauthorized_account()
            if account:
                current_status = get_unauthorized_queue_status()
                print(f"[API] get_unauthorized_account: Success, account={account.email_account}, remaining={current_status['queue_size']}")
                return jsonify({
                    'success': True,
                    'account': account.to_dict(),
                    'remaining_accounts': current_status['queue_size']
                })
            else:
                print("[API] get_unauthorized_account: Queue empty")
                return jsonify({
                    'success': False,
                    'message': '未认证账户队列已空',
                    'remaining_accounts': 0
                }), 404
        except Exception as e:
            print(f"[API] get_unauthorized_account Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/load_single_authorized_account', methods=['GET'])
    def load_single_authorized_account_api():
        """加载指定表格的指定行账户数据（手动加载）"""
        sheetid = request.args.get('sheetid')
        spreadsheetToken = request.args.get('spreadsheetToken')
        row_num = request.args.get('row_num')

        if not all([sheetid, spreadsheetToken, row_num]):
            return jsonify({
                'success': False,
                'message': '参数缺失，请提供sheetid、spreadsheetToken、row_num'
            }), 400

        try:
            success, msg = load_single_authorized_account(
                sheet_id=sheetid,
                spreadsheet_token=spreadsheetToken,
                row_num=row_num
            )
            
            if success:
                current_status = get_account_queue_status()
                return jsonify({
                    'success': True,
                    'message': msg,
                    'current_queue_size': current_status['queue_size']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': msg
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'接口调用异常：{str(e)}'
            }), 500

    # ---------------- 新增：更新飞书表格流程追踪列（J列）接口（严格遵循文档） ----------------
    @app.route('/update_process_tracing_column', methods=['GET'])
    def update_process_tracing_column():
        """
        更新飞书表格J列（流程追踪）的指定行内容
        """
        sheetid = request.args.get('sheetid')
        spreadsheet_token = request.args.get('spreadsheettoken')
        row_num = request.args.get('row_num')
        content = request.args.get('content')

        if not all([sheetid, spreadsheet_token, row_num, content]):
            return jsonify({
                'success': False,
                'message': '参数缺失，请提供sheetid、spreadsheettoken、row_num、content',
                'error_detail': 'URL格式示例：/update_process_tracing_column?sheetid=3eb130&spreadsheettoken=ZmTWwo0VHiOXakk5M3PcEOKonzb&row_num=2&content=已处理'
            }), 400

        try:
            cell_range = f"{sheetid}!J{row_num}:J{row_num}"
            update_result = update_feishu_sheet_cell(
                sheet_id=sheetid,
                spreadsheet_token=spreadsheet_token,
                cell_range=cell_range,
                content=content
            )

            if update_result:
                return jsonify({
                    'success': True,
                    'message': '流程追踪列内容更新成功',
                    'target_cell': cell_range,
                    'written_content': content
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '流程追踪列内容更新失败，请查看服务端终端日志',
                    'target_cell': cell_range
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'更新过程出现异常：{str(e)}',
                'target_cell': f"{sheetid}!J{row_num}:J{row_num}"
            }), 500

    @app.route('/update_order_window_num', methods=['GET'])
    def update_order_window_num():
        """
        更新飞书表格N列（确认订单比特窗口号）的指定行内容
        """
        sheetid = request.args.get('sheetid')
        spreadsheet_token = request.args.get('spreadsheettoken')
        row_num = request.args.get('row_num')
        window_num = request.args.get('window_num')

        if not all([sheetid, spreadsheet_token, row_num, window_num]):
            return jsonify({
                'success': False,
                'message': '参数缺失，请提供sheetid、spreadsheettoken、row_num、window_num',
                'error_detail': 'URL格式示例：/update_order_window_num?sheetid=...&spreadsheettoken=...&row_num=...&window_num=...'
            }), 400

        try:
            cell_range = f"{sheetid}!N{row_num}:N{row_num}"
            update_result = update_feishu_sheet_cell(
                sheet_id=sheetid,
                spreadsheet_token=spreadsheet_token,
                cell_range=cell_range,
                content=window_num
            )

            if update_result:
                return jsonify({
                    'success': True,
                    'message': '订单窗口号更新成功',
                    'target_cell': cell_range,
                    'written_content': window_num
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '订单窗口号更新失败，请查看服务端终端日志',
                    'target_cell': cell_range
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'更新过程出现异常：{str(e)}',
                'target_cell': f"{sheetid}!N{row_num}:N{row_num}"
            }), 500

    @app.route('/get_authorized_account', methods=['GET'])
    def get_authorized_account_api():
        """获取单个已认证账户（从Authorized队列）"""
        try:
            print("[API] get_authorized_account: Request received")
            account = get_authorized_account()
            if account:
                current_status = get_authorized_queue_status()
                print(f"[API] get_authorized_account: Success, account={account.email_account}, remaining={current_status['queue_size']}")
                return jsonify({
                    'success': True,
                    'account': account.to_dict(),
                    'remaining_accounts': current_status['queue_size']
                })
            else:
                print("[API] get_authorized_account: Queue empty")
                return jsonify({
                    'success': False,
                    'message': '已认证账户队列已空',
                    'remaining_accounts': 0
                }), 404
        except Exception as e:
            print(f"[API] get_authorized_account Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/get_authorized_account_status', methods=['GET'])
    def get_authorized_account_status_api():
        try:
            status = get_authorized_queue_status()
            print(f"[API] get_authorized_account_status: size={status['queue_size']}")
            return jsonify({
                'success': True,
                'queue_size': status['queue_size'],
                'is_empty': status['is_empty']
            })
        except Exception as e:
            print(f"[API] get_authorized_account_status Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/get_unauthorized_account_status', methods=['GET'])
    def get_unauthorized_account_status_api():
        try:
            status = get_unauthorized_queue_status()
            print(f"[API] get_unauthorized_account_status: size={status['queue_size']}")
            return jsonify({
                'success': True,
                'queue_size': status['queue_size'],
                'is_empty': status['is_empty']
            })
        except Exception as e:
            print(f"[API] get_unauthorized_account_status Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/reset_unauthorized_accounts', methods=['GET'])
    def reset_unauthorized_accounts_api():
        """重置Unauthorized账户队列和去重记录"""
        try:
            reset_unauthorized_queue_and_emails()
            return jsonify({
                'success': True,
                'message': 'Unauthorized账户队列和已加载邮箱记录已重置'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'重置失败：{str(e)}'
            }), 500

    @app.route('/reset_authorized_accounts', methods=['GET'])
    def reset_authorized_accounts_api():
        """重置Authorized账户队列和去重记录"""
        try:
            reset_authorized_queue_and_emails()
            return jsonify({
                'success': True,
                'message': 'Authorized账户队列和已加载邮箱记录已重置'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'重置失败：{str(e)}'
            }), 500

    # ---------------- 新增：Offline 账户接口 ----------------
    @app.route('/load_offline_accounts', methods=['GET'])
    def load_offline_accounts():
        """加载所有表格的离线账户（J列='使用过程中被弹出'）"""
        try:
            loaded_count = load_all_offline_accounts()
            current_status = get_offline_queue_status()
            return jsonify({
                'success': True,
                'message': '离线账户表格加载完成',
                'total_loaded_accounts': loaded_count,
                'current_account_queue_size': current_status['queue_size']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'加载失败：{str(e)}'
            }), 500

    @app.route('/load_offline_accounts_from', methods=['GET'])
    def load_offline_accounts_from():
        """加载指定表格的离线账户"""
        sheetid = request.args.get('sheetid')
        spreadsheetToken = request.args.get('spreadsheetToken')

        if not sheetid or not spreadsheetToken:
            return jsonify({
                'success': False,
                'message': '参数缺失，请同时提供sheetid和spreadsheetToken',
                'error_detail': 'URL格式示例：/load_offline_accounts_from?sheetid=3eb130&spreadsheetToken=xxx'
            }), 400

        try:
            loaded_count = load_offline_accounts_from_sheet(sheetid, spreadsheetToken)
            current_status = get_offline_queue_status()
            return jsonify({
                'success': True,
                'message': '指定表格离线账户加载完成',
                'target_sheetid': sheetid,
                'total_loaded_accounts': loaded_count,
                'current_account_queue_size': current_status['queue_size']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'加载失败：{str(e)}',
                'target_sheetid': sheetid
            }), 500

    @app.route('/get_offline_account', methods=['GET'])
    def get_offline_account_api():
        """获取单个离线账户"""
        try:
            print("[API] get_offline_account: Request received")
            account = get_offline_account()
            if account:
                current_status = get_offline_queue_status()
                print(f"[API] get_offline_account: Success, account={account.email_account}, remaining={current_status['queue_size']}")
                return jsonify({
                    'success': True,
                    'account': account.to_dict(),
                    'remaining_accounts': current_status['queue_size']
                })
            else:
                print("[API] get_offline_account: Queue empty")
                return jsonify({
                    'success': False,
                    'message': '离线账户队列已空',
                    'remaining_accounts': 0
                }), 404
        except Exception as e:
            print(f"[API] get_offline_account Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/get_offline_account_status', methods=['GET'])
    def get_offline_account_status_api():
        """查看离线账户队列状态"""
        try:
            status = get_offline_queue_status()
            print(f"[API] get_offline_account_status: size={status['queue_size']}")
            return jsonify({
                'success': True,
                'queue_size': status['queue_size'],
                'is_empty': status['is_empty']
            })
        except Exception as e:
            print(f"[API] get_offline_account_status Error: {str(e)}")
            traceback.print_exc()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/reset_offline_accounts', methods=['GET'])
    def reset_offline_accounts_api():
        """重置Offline账户队列和去重记录"""
        try:
            reset_offline_queue_and_emails()
            return jsonify({
                'success': True,
                'message': 'Offline账户队列和已加载邮箱记录已重置'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'重置失败：{str(e)}'
            }), 500

    # ---------------- 新增：终端截图上传接口 ----------------
    @app.route('/upload_screenshot', methods=['POST'])
    def upload_screenshot():
        """接收终端机上传的截图，更新内存缓存（覆盖旧值）"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            data = request.get_json()
            terminal_id = data.get("terminal_id")
            print(f"[{current_time}] ℹ️  接收到截图上传请求 - 终端ID：{terminal_id if terminal_id else '未知'}，请求体：{data.keys() if data else '空'}")

            if not all([terminal_id, data.get("screenshot_base64"), data.get("update_time")]):
                err_msg = "参数缺失：terminal_id、screenshot_base64、update_time 必填"
                print(f"[{current_time}] ❌  截图上传失败 - {err_msg}")
                return jsonify({
                    "success": False,
                    "message": err_msg
                }), 400

            update_screenshot_cache(terminal_id, data.get("screenshot_base64"), data.get("update_time"))
            print(f"[{current_time}] ✅  截图上传成功 - 终端ID：{terminal_id}")

            return jsonify({
                "success": True,
                "message": "截图缓存更新成功",
                "terminal_id": terminal_id
            })
        except Exception as e:
            err_msg = f"截图上传失败：{str(e)}"
            print(f"[{current_time}] ❌  截图上传异常 - {err_msg}")
            return jsonify({
                "success": False,
                "message": err_msg
            }), 500

    @app.route('/get_all_latest_screenshots', methods=['GET'])
    def get_all_latest_screenshots():
        """返回所有终端的最新截图缓存（仅存最新一次）"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            print(f"[{current_time}] ℹ️  接收到截图轮询请求 - 来源：项目C（客户机）")
            screenshot_list = get_all_screenshot_cache()
            print(f"[{current_time}] ✅  截图轮询响应成功 - 返回终端数：{len(screenshot_list)}")

            return jsonify({
                "success": True,
                "screenshot_count": len(screenshot_list),
                "screenshots": screenshot_list,
                "server_time": current_time
            })
        except Exception as e:
            err_msg = f"获取截图缓存失败：{str(e)}"
            print(f"[{current_time}] ❌  截图轮询异常 - {err_msg}")
            return jsonify({
                "success": False,
                "message": err_msg
            }), 500

    @app.route('/clear_screenshot_cache', methods=['GET'])
    def clear_screenshot_cache_api():
        """清空所有终端的截图缓存（访问一次即可完成清空）"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cleared_count = clear_screenshot_cache()
            return jsonify({
                "success": True,
                "message": f"截图缓存已成功清空",
                "cleared_terminal_count": cleared_count,
                "operation_time": current_time
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"清空截图缓存失败：{str(e)}",
                "operation_time": current_time
            }), 500

    @app.route('/get_screenshot_list', methods=['GET'])
    def get_screenshot_list_api():
        """获取终端ID列表（不含截图内容，用于分批获取优化）"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            terminal_list = get_screenshot_list()
            return jsonify({
                "success": True,
                "terminal_count": len(terminal_list),
                "terminals": terminal_list,
                "server_time": current_time
            })
        except Exception as e:
            err_msg = f"获取终端列表失败：{str(e)}"
            print(f"[{current_time}] ❌  获取终端列表异常 - {err_msg}")
            return jsonify({
                "success": False,
                "message": err_msg
            }), 500

    @app.route('/get_screenshot_by_id', methods=['GET'])
    def get_screenshot_by_id_api():
        """获取指定终端的截图"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        terminal_id = request.args.get('terminal_id')
        
        if not terminal_id:
            return jsonify({
                "success": False,
                "message": "参数缺失：terminal_id 必填"
            }), 400
        
        try:
            screenshot = get_screenshot_by_id(terminal_id)
            if screenshot:
                return jsonify({
                    "success": True,
                    "screenshot": screenshot,
                    "server_time": current_time
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"终端 {terminal_id} 的截图不存在"
                }), 404
        except Exception as e:
            err_msg = f"获取截图失败：{str(e)}"
            print(f"[{current_time}] ❌  获取单个截图异常 - {err_msg}")
            return jsonify({
                "success": False,
                "message": err_msg
            }), 500

    @app.route('/get_screenshot_cache_status', methods=['GET'])
    def get_screenshot_cache_status_api():
        """获取截图缓存状态"""
        try:
            status = get_cache_status()
            return jsonify({
                "success": True,
                "cache_status": status
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"获取缓存状态失败：{str(e)}"
            }), 500
