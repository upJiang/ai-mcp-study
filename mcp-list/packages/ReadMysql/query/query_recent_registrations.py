#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查询最近7天的用户注册情况"""

from ..mysql_api import MySQLAPI
from datetime import datetime, timedelta

def query_recent_registrations():
    """查询最近7天的用户注册情况"""
    database = "master_3d66_data"
    table = "ll_user"

    print(f"=== 最近7天注册用户统计 ===\n")

    try:
        # 查询最近7天每天的注册数
        query = """
        SELECT
            DATE(FROM_UNIXTIME(created_at)) as reg_date,
            COUNT(*) as count
        FROM ll_user
        WHERE created_at >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 7 DAY))
        GROUP BY DATE(FROM_UNIXTIME(created_at))
        ORDER BY reg_date DESC
        """

        result = MySQLAPI.execute_query(database, query)

        if result['success']:
            print("日期          注册用户数")
            print("-" * 30)
            total = 0
            for row in result['data']:
                count = row['count']
                total += count
                print(f"{row['reg_date']}    {count:,} 人")

            print("-" * 30)
            print(f"总计:         {total:,} 人\n")

            # 查询今天的具体时间
            today = datetime.now().strftime('%Y-%m-%d')
            today_query = f"""
            SELECT
                id,
                FROM_UNIXTIME(created_at) as registration_time
            FROM ll_user
            WHERE DATE(FROM_UNIXTIME(created_at)) = '{today}'
            ORDER BY created_at DESC
            LIMIT 10
            """

            print(f"\n今天 ({today}) 注册的用户详情:\n")
            today_result = MySQLAPI.execute_query(database, today_query)

            if today_result['success'] and today_result['data']:
                for i, user in enumerate(today_result['data'], 1):
                    print(f"  {i}. 用户ID: {user.get('id')}, 注册时间: {user.get('registration_time')}")
            else:
                print("  今天暂无注册用户")

        else:
            print(f"[FAIL] 查询失败: {result.get('error')}")

    except Exception as e:
        print(f"[ERROR] 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    query_recent_registrations()
