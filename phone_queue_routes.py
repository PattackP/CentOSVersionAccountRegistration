# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
# phone_queue_routes.py
# 手机号队列接口
from flask import jsonify, request
from feishu_api import update_feishu_sheet_cell
from phone_queue_manager import (
    load_phone_queue,
    get_phone_data,
    put_back_phone_data,
    get_phone_queue_status
)


def register_phone_queue_routes(app):
    """注册手机号队列路由"""

    @app.route('/load_phone_queue', methods=['GET'])
    def load_phone_queue_api():
        """加载手机号队列（从表格253571读取数据）"""
        try:
            loaded_count = load_phone_queue()
            status = get_phone_queue_status()
            return jsonify({
                'success': True,
                'message': '手机号队列加载完成',
                'loaded_count': loaded_count,
                'queue_size': status['queue_size']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'加载失败：{str(e)}'
            }), 500

    @app.route('/get_phone_data', methods=['GET'])
    def get_phone_data_api():
        """从队列取出一条手机号数据（FIFO）"""
        try:
            data = get_phone_data()
            if data:
                status = get_phone_queue_status()
                return jsonify({
                    'success': True,
                    'data': data,
                    'remaining': status['queue_size']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '队列为空',
                    'remaining': 0
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/put_back_phone_data', methods=['GET'])
    def put_back_phone_data_api():
        """把未消费成功的数据放回队列"""
        row_num = request.args.get('row_num')
        sheetid = request.args.get('sheetid')
        spreadsheettoken = request.args.get('spreadsheettoken')
        phone_number = request.args.get('phone_number')
        sms_url = request.args.get('sms_url')

        if not all([row_num, sheetid, spreadsheettoken, phone_number]):
            return jsonify({
                'success': False,
                'message': '参数缺失，请提供row_num、sheetid、spreadsheettoken、phone_number',
                'error_detail': 'URL格式示例：/put_back_phone_data?row_num=2&sheetid=xxx&spreadsheettoken=xxx&phone_number=xxx&sms_url=xxx'
            }), 400

        try:
            put_back_phone_data(row_num, sheetid, spreadsheettoken, phone_number, sms_url or "")
            status = get_phone_queue_status()
            return jsonify({
                'success': True,
                'message': '数据已放回队列',
                'queue_size': status['queue_size']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/update_window_name', methods=['GET'])
    def update_window_name_api():
        """在指定表格F列对应行写入窗口名称"""
        row_num = request.args.get('row_num')
        sheetid = request.args.get('sheetid')
        spreadsheettoken = request.args.get('spreadsheettoken')
        window_name = request.args.get('window_name')

        if not all([row_num, sheetid, spreadsheettoken, window_name]):
            return jsonify({
                'success': False,
                'message': '参数缺失，请提供row_num、sheetid、spreadsheettoken、window_name',
                'error_detail': 'URL格式示例：/update_window_name?row_num=2&sheetid=xxx&spreadsheettoken=xxx&window_name=xxx'
            }), 400

        try:
            cell_range = f"{sheetid}!F{row_num}:F{row_num}"
            update_result = update_feishu_sheet_cell(
                sheet_id=sheetid,
                spreadsheet_token=spreadsheettoken,
                cell_range=cell_range,
                content=window_name
            )

            if update_result:
                return jsonify({
                    'success': True,
                    'message': '窗口名称写入成功',
                    'target_cell': cell_range,
                    'written_content': window_name
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '窗口名称写入失败',
                    'target_cell': cell_range
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    @app.route('/phone_queue_status', methods=['GET'])
    def phone_queue_status_api():
        """查看手机号队列状态"""
        try:
            status = get_phone_queue_status()
            return jsonify({
                'success': True,
                'queue_size': status['queue_size'],
                'is_empty': status['is_empty']
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
