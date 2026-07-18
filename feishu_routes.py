# -*- coding: utf-8 -*-  # CentOS下强制指定UTF-8编码，避免中文乱码
# feishu_routes.py
# 飞书表格读写接口
from flask import jsonify, request
from feishu_api import update_feishu_sheet_cell, _fetch_feishu_sheet_data


def register_feishu_routes(app):
    """注册飞书表格读写路由"""

    @app.route('/read_sheet_data', methods=['GET'])
    def read_sheet_data():
        """读取飞书表格数据"""
        sheetid = request.args.get('sheetid')
        spreadsheet_token = request.args.get('spreadsheettoken')
        range_str = request.args.get('range', 'A:J')

        if not all([sheetid, spreadsheet_token]):
            return jsonify({
                'success': False,
                'message': '参数缺失，请提供sheetid、spreadsheettoken',
                'error_detail': 'URL格式示例：/read_sheet_data?sheetid=3eb130&spreadsheettoken=xxx&range=A:J'
            }), 400

        try:
            data = _fetch_feishu_sheet_data(sheetid, spreadsheet_token, range_str)
            if data is not None:
                return jsonify({
                    'success': True,
                    'message': '表格数据读取成功',
                    'row_count': len(data),
                    'data': data
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '表格数据读取失败，请查看服务端终端日志'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'读取过程出现异常：{str(e)}'
            }), 500

    @app.route('/update_cell', methods=['GET'])
    def update_cell():
        """更新飞书表格指定单元格内容"""
        sheetid = request.args.get('sheetid')
        spreadsheet_token = request.args.get('spreadsheettoken')
        cell_range = request.args.get('cell_range')
        content = request.args.get('content')

        if not all([sheetid, spreadsheet_token, cell_range, content]):
            return jsonify({
                'success': False,
                'message': '参数缺失，请提供sheetid、spreadsheettoken、cell_range、content',
                'error_detail': 'URL格式示例：/update_cell?sheetid=3eb130&spreadsheettoken=xxx&cell_range=3eb130!J2:J2&content=已处理'
            }), 400

        try:
            update_result = update_feishu_sheet_cell(
                sheet_id=sheetid,
                spreadsheet_token=spreadsheet_token,
                cell_range=cell_range,
                content=content
            )

            if update_result:
                return jsonify({
                    'success': True,
                    'message': '单元格内容更新成功',
                    'target_cell': cell_range,
                    'written_content': content
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '单元格内容更新失败，请查看服务端终端日志',
                    'target_cell': cell_range
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'更新过程出现异常：{str(e)}',
                'target_cell': cell_range
            }), 500

    @app.route('/update_process_tracing_column', methods=['GET'])
    def update_process_tracing_column():
        """更新飞书表格J列（流程追踪）的指定行内容"""
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
        """更新飞书表格N列（确认订单比特窗口号）的指定行内容"""
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
