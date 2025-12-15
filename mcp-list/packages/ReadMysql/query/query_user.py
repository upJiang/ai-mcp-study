#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查询 ll_user 表"""

from ..mysql_api import MySQLAPI
import json

def query_user_table():
    """查询 ll_user 表的数据"""
    database = "master_3d66_data"
    table = "ll_user"

    print(f"=== 查询 {database}.{table} 表 ===\n")

    try:
        # 1. 查看表结构
        print("1. 表结构:")
        structure = MySQLAPI.describe_table(database, table)
        print(f"共 {len(structure)} 个字段:\n")
        for field in structure:
            null_str = "NULL" if field['Null'] == 'YES' else "NOT NULL"
            key_str = f" [{field['Key']}]" if field['Key'] else ""
            default_str = f" DEFAULT {field['Default']}" if field['Default'] else ""
            extra_str = f" {field['Extra']}" if field['Extra'] else ""
            print(f"  {field['Field']:<30} {field['Type']:<20} {null_str:<10}{key_str}{default_str}{extra_str}")

        print("\n" + "="*80 + "\n")

        # 2. 查询总行数
        result = MySQLAPI.execute_query(database, f"SELECT COUNT(*) as total FROM `{table}`")
        if result['success']:
            total = result['data'][0]['total']
            print(f"2. 总记录数: {total:,}\n")

        print("="*80 + "\n")

        # 3. 查询前 5 条数据
        print("3. 前 5 条记录:\n")
        result = MySQLAPI.execute_query(database, f"SELECT * FROM `{table}` LIMIT 5")

        if result['success']:
            print(f"查询成功，返回 {result['row_count']} 行\n")
            print(f"字段列表: {', '.join(result['columns'])}\n")

            for i, row in enumerate(result['data'], 1):
                print(f"--- 记录 {i} ---")
                for key, value in row.items():
                    # 格式化显示
                    if isinstance(value, (dict, list)):
                        value_str = json.dumps(value, ensure_ascii=False)
                    else:
                        value_str = str(value) if value is not None else "NULL"

                    # 限制显示长度
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."

                    print(f"  {key:<30}: {value_str}")
                print()
        else:
            print(f"查询失败: {result.get('error')}")

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    query_user_table()
