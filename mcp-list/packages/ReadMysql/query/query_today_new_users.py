#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查询今天新增的用户"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mysql_api import MySQLAPI
from datetime import datetime
import json

def query_today_new_users(limit=20):
    """查询今天新增的用户"""
    today = datetime.now().strftime('%Y-%m-%d')

    # 查询今天新增的用户数
    query_count = f"""
    SELECT COUNT(*) as today_count
    FROM ll_user
    WHERE DATE(FROM_UNIXTIME(reg_time)) = '{today}'
    """

    result_count = MySQLAPI.execute_query('master_3d66_user', query_count, tool_name='count_today_users')

    if not result_count['success']:
        print(json.dumps({
            "success": False,
            "error": result_count.get('error')
        }, ensure_ascii=False, indent=2))
        return

    total_count = result_count['data'][0]['today_count']

    # 查询今天新增的用户详情
    query_detail = f"""
    SELECT
        user_id,
        user_name,
        nick_name,
        user_tel,
        user_email,
        user_qq,
        user_province,
        user_city,
        FROM_UNIXTIME(reg_time) as registration_time,
        reg_time
    FROM ll_user
    WHERE DATE(FROM_UNIXTIME(reg_time)) = '{today}'
    ORDER BY reg_time DESC
    LIMIT {limit}
    """

    result_detail = MySQLAPI.execute_query('master_3d66_user', query_detail, tool_name='get_today_users_detail')

    if not result_detail['success']:
        print(json.dumps({
            "success": False,
            "error": result_detail.get('error')
        }, ensure_ascii=False, indent=2))
        return

    # 输出结果
    output = {
        "success": True,
        "date": today,
        "total_new_users": total_count,
        "showing": len(result_detail['data']),
        "users": []
    }

    for user in result_detail['data']:
        output['users'].append({
            "user_id": user.get('user_id'),
            "user_name": user.get('user_name') or None,
            "nick_name": user.get('nick_name') or None,
            "user_tel": user.get('user_tel') or None,
            "user_email": user.get('user_email') or None,
            "user_qq": user.get('user_qq') or None,
            "location": f"{user.get('user_province') or ''} {user.get('user_city') or ''}".strip() or None,
            "registration_time": str(user.get('registration_time')),
            "reg_timestamp": user.get('reg_time')
        })

    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    query_today_new_users(limit)
