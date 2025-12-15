#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查询用户余额总和"""

from ..mysql_api import MySQLAPI

# 查询余额总和
sql = """
SELECT
    SUM(web_res_consume) as total_web_res,
    SUM(convert_xuandian) as total_convert,
    SUM(recharge_lb) as total_recharge,
    SUM(return_lb) as total_return,
    SUM(lottery_lb) as total_lottery,
    SUM(income_lb) as total_income,
    SUM(user_merge_lb) as total_user_merge,
    SUM(transfer_lb) as total_transfer
FROM ll_census_user_lb
"""

try:
    result = MySQLAPI.execute_query('master_3d66_census', sql)

    if result and result.get('success') and result.get('data'):
        data = result['data'][0]

        print("\n======= 用户余额统计结果 =======\n")
        print(f"网页资源消费总额: {int(data['total_web_res'] or 0):,}")
        print(f"转换炫点总额:     {int(data['total_convert'] or 0):,}")
        print(f"充值余额总额:     {int(data['total_recharge'] or 0):,}")
        print(f"返还余额总额:     {int(data['total_return'] or 0):,}")
        print(f"抽奖余额总额:     {int(data['total_lottery'] or 0):,}")
        print(f"收入余额总额:     {int(data['total_income'] or 0):,}")
        print(f"用户合并余额:     {int(data['total_user_merge'] or 0):,}")
        print(f"转账余额总额:     {int(data['total_transfer'] or 0):,}")
        print("\n================================\n")
    else:
        print("未查询到数据")
        if result and not result.get('success'):
            print(f"错误信息: {result.get('error')}")

except Exception as e:
    import traceback
    print(f"查询失败: {e}")
    traceback.print_exc()
