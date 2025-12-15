#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查询今天的充值总和"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database.operations import DatabaseOperations
from core.connection_pool import ConnectionPool
from config.settings import get_settings

def query_today_recharge():
    """查询今天的充值数据"""
    # 初始化
    settings = get_settings()
    pool = ConnectionPool()
    pool.initialize(settings)
    db_ops = DatabaseOperations(pool)

    # 获取今天的日期
    today = datetime.now().strftime('%Y-%m-%d')

    # 查询今天的充值总和
    query = f"""
    SELECT
        COUNT(*) as order_count,
        SUM(total_fee) as total_amount,
        MIN(total_fee) as min_amount,
        MAX(total_fee) as max_amount,
        AVG(total_fee) as avg_amount
    FROM ll_recharge_success
    WHERE DATE(FROM_UNIXTIME(cz_time)) = '{today}'
    """

    result = db_ops.execute_query('master_3d66_user', query, tool_name='query_today_recharge_total')

    if result['success'] and result['data']:
        import json
        from decimal import Decimal

        data = result['data'][0]

        # 转换 Decimal 为 float 以便 JSON 序列化
        output = {
            'date': today,
            'order_count': data['order_count'],
            'total_amount': float(data['total_amount']) if data['total_amount'] else 0,
            'min_amount': float(data['min_amount']) if data['min_amount'] else 0,
            'max_amount': float(data['max_amount']) if data['max_amount'] else 0,
            'avg_amount': float(data['avg_amount']) if data['avg_amount'] else 0
        }

        print(json.dumps(output, ensure_ascii=False, indent=2))
        return data
    else:
        import json
        print(json.dumps({'success': False, 'error': result.get('error', '未知错误')}, ensure_ascii=False, indent=2))
        return None

if __name__ == "__main__":
    query_today_recharge()
