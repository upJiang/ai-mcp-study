#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查看查询日志统计"""

import sys
from datetime import datetime
from pathlib import Path

# 添加父目录到路径以便导入核心模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.query_logger import get_logger


def view_statistics(date: str = None):
    """
    查看指定日期的查询统计

    Args:
        date: 日期（格式：YYYYMMDD），默认为今天
    """
    logger = get_logger()

    if date is None:
        date = datetime.now().strftime('%Y%m%d')

    print(f"\n{'='*60}")
    print(f"  查询统计报告 - {date[:4]}-{date[4:6]}-{date[6:]}")
    print(f"{'='*60}\n")

    stats = logger.get_statistics(date)

    # 基本统计
    print("基本统计:")
    print(f"  总查询次数:     {stats['total_queries']:>6}")
    print(f"  成功查询:       {stats['successful_queries']:>6}")
    print(f"  失败查询:       {stats['failed_queries']:>6}")
    print(f"  总返回行数:     {stats['total_rows']:>6,}")
    print(f"  总执行时间:     {stats['total_time']:>6.2f} 秒")

    if stats['total_queries'] > 0:
        avg_time = stats['total_time'] / stats['total_queries']
        avg_rows = stats['total_rows'] / stats['total_queries']
        success_rate = (stats['successful_queries'] / stats['total_queries']) * 100

        print(f"\n平均统计:")
        print(f"  平均执行时间:   {avg_time:>6.4f} 秒/查询")
        print(f"  平均返回行数:   {avg_rows:>6.1f} 行/查询")
        print(f"  成功率:         {success_rate:>6.1f}%")

    # 数据库统计
    if stats.get('databases'):
        print(f"\n按数据库统计:")
        for db, count in sorted(stats['databases'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {db:<30} {count:>6} 次查询")

    # 工具统计
    if stats.get('tools'):
        print(f"\n按工具统计:")
        for tool, count in sorted(stats['tools'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {tool:<30} {count:>6} 次调用")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    # 从命令行参数获取日期
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    view_statistics(date_arg)
