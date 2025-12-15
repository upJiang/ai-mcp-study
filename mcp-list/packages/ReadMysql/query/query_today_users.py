#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""统计今天注册的用户数"""

from ..mysql_api import MySQLAPI
from datetime import datetime

def query_today_registered_users():
    """统计今天注册的用户数"""
    database = "master_3d66_data"
    table = "ll_user"
    today = datetime.now().strftime('%Y-%m-%d')

    print(f"=== 统计 {today} 注册的用户数 ===\n")

    try:
        # 查询今天注册的用户数（假设注册时间字段是 created_at 或 create_time 或 reg_time）
        # 先尝试几个常见的时间字段名
        time_fields = ['created_at', 'create_time', 'reg_time', 'register_time', 'add_time']

        # 先获取表结构，确定时间字段
        print("1. 获取表结构...")
        structure = MySQLAPI.describe_table(database, table)

        # 查找可能的时间字段
        time_field = None
        for field in structure:
            field_name = field['Field'].lower()
            if any(tf in field_name for tf in ['create', 'reg', 'add']) and any(tf in field_name for tf in ['time', 'date', 'at']):
                time_field = field['Field']
                print(f"   找到时间字段: {time_field} ({field['Type']})\n")
                break

        if not time_field:
            print("   未找到明确的时间字段，将列出所有字段供参考:\n")
            for field in structure:
                print(f"   - {field['Field']:<30} {field['Type']}")
            return

        # 查询今天注册的用户数
        # 判断字段类型，如果是 int 类型则使用 FROM_UNIXTIME 转换
        field_type = None
        for field in structure:
            if field['Field'] == time_field:
                field_type = field['Type']
                break

        # 根据字段类型构建查询条件
        if 'int' in field_type.lower():
            # Unix 时间戳类型
            date_condition = f"DATE(FROM_UNIXTIME(`{time_field}`)) = '{today}'"
        else:
            # 日期时间类型
            date_condition = f"DATE(`{time_field}`) = '{today}'"

        query = f"""
        SELECT COUNT(*) as today_count
        FROM `{table}`
        WHERE {date_condition}
        """

        print(f"2. 执行查询: {query.strip()}\n")
        result = MySQLAPI.execute_query(database, query)

        if result['success']:
            count = result['data'][0]['today_count']
            print(f"[OK] 今天 ({today}) 注册用户数: {count:,} 人\n")

            # 额外查询：显示今天注册的前几个用户
            detail_query = f"""
            SELECT *
            FROM `{table}`
            WHERE {date_condition}
            ORDER BY `{time_field}` DESC
            LIMIT 5
            """

            print(f"3. 今天注册的前 5 个用户:\n")
            detail_result = MySQLAPI.execute_query(database, detail_query)

            if detail_result['success'] and detail_result['data']:
                for i, user in enumerate(detail_result['data'], 1):
                    print(f"   {i}. 用户ID: {user.get('id', 'N/A')}, 注册时间: {user.get(time_field, 'N/A')}")
            else:
                print("   今天暂无注册用户")
        else:
            print(f"[FAIL] 查询失败: {result.get('error')}")

    except Exception as e:
        print(f"[ERROR] 错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    query_today_registered_users()
