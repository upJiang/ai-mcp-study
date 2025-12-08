#!/usr/bin/env python3
"""Claude Stats MCP Server - Python Implementation"""

import os
import sys
import json
import asyncio
from datetime import date, datetime
from typing import Optional
from fastmcp import FastMCP
from dotenv import load_dotenv

from utils.config_loader import load_api_keys
from utils.api_client import get_all_key_stats, KeyStatsResult
from utils.data_analyzer import (
    format_cost,
    format_tokens,
    get_top_users,
    find_user_by_name,
    compare_users,
    detect_anomalies,
    generate_summary,
    calculate_usage_percentage
)

# 加载环境变量
load_dotenv()

# 创建FastMCP实例
mcp = FastMCP(
    name="Claude Stats MCP",
    instructions="""
这是一个用于查询Claude Code使用统计的MCP服务器（Python版本）。

可用工具：
1. query_today_stats - 查询今日所有账号统计
2. query_monthly_stats - 查询本月所有账号统计
3. query_user_stats - 查询特定用户统计
4. query_top_users - 查询使用率最高的用户
5. compare_users - 比较两个用户的使用情况
6. analyze_usage_trend - 分析使用趋势
7. detect_anomalies - 检测异常使用情况
8. generate_report - 生成完整的使用报告

使用示例：
- "今天使用率最高的是谁？" -> 使用 query_top_users
- "查询江俊锋的今日使用情况" -> 使用 query_user_stats
- "对比江俊锋和陈雷的使用情况" -> 使用 compare_users
    """.strip()
)

# 缓存数据
daily_stats_cache = None
monthly_stats_cache = None
last_daily_fetch = 0
last_monthly_fetch = 0
CACHE_TTL = 5 * 60  # 5分钟缓存（秒）


async def get_daily_stats(force_refresh: bool = False):
    """获取今日统计（带缓存）"""
    global daily_stats_cache, last_daily_fetch
    
    now = asyncio.get_event_loop().time()
    if not force_refresh and daily_stats_cache and (now - last_daily_fetch) < CACHE_TTL:
        return daily_stats_cache
    
    api_keys = load_api_keys()
    stats = await get_all_key_stats(api_keys, 'daily')
    daily_stats_cache = stats
    last_daily_fetch = now
    return stats


async def get_monthly_stats(force_refresh: bool = False):
    """获取本月统计（带缓存）"""
    global monthly_stats_cache, last_monthly_fetch
    
    now = asyncio.get_event_loop().time()
    if not force_refresh and monthly_stats_cache and (now - last_monthly_fetch) < CACHE_TTL:
        return monthly_stats_cache
    
    api_keys = load_api_keys()
    stats = await get_all_key_stats(api_keys, 'monthly')
    monthly_stats_cache = stats
    last_monthly_fetch = now
    return stats


@mcp.tool()
async def query_today_stats(force_refresh: bool = False) -> str:
    """
    查询今日所有账号的使用统计
    
    Args:
        force_refresh: 是否强制刷新缓存数据（默认False）
    
    Returns:
        JSON格式的统计数据
    """
    try:
        stats = await get_daily_stats(force_refresh)
        summary = generate_summary(stats)
        
        result = {
            'period': '今日统计',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'totalUsers': summary['total_users'],
                'activeUsers': summary['active_users'],
                'totalCost': format_cost(summary['total_cost']),
                'totalRequests': f"{summary['total_requests']:,}",
                'totalTokens': format_tokens(summary['total_tokens']),
                'avgCostPerUser': format_cost(summary['avg_cost_per_user'])
            },
            'users': [
                {
                    'name': s.name,
                    'account': s.account,
                    'cost': format_cost(s.stats.totalCost),
                    'requests': s.stats.requests,
                    'tokens': format_tokens(s.stats.allTokens),
                    'usagePercent': calculate_usage_percentage(s.stats.totalCost, 40) + '%'
                }
                for s in stats if s.success
            ],
            'failedUsers': [
                {
                    'name': s.name,
                    'account': s.account,
                    'error': s.error
                }
                for s in stats if not s.success
            ]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def query_monthly_stats(force_refresh: bool = False) -> str:
    """
    查询本月所有账号的使用统计
    
    Args:
        force_refresh: 是否强制刷新缓存数据（默认False）
    
    Returns:
        JSON格式的统计数据
    """
    try:
        stats = await get_monthly_stats(force_refresh)
        summary = generate_summary(stats)
        
        result = {
            'period': '本月统计',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'totalUsers': summary['total_users'],
                'activeUsers': summary['active_users'],
                'totalCost': format_cost(summary['total_cost']),
                'totalRequests': f"{summary['total_requests']:,}",
                'totalTokens': format_tokens(summary['total_tokens']),
                'avgCostPerUser': format_cost(summary['avg_cost_per_user'])
            },
            'users': [
                {
                    'name': s.name,
                    'account': s.account,
                    'cost': format_cost(s.stats.totalCost),
                    'requests': s.stats.requests,
                    'tokens': format_tokens(s.stats.allTokens)
                }
                for s in stats if s.success
            ],
            'failedUsers': [
                {
                    'name': s.name,
                    'account': s.account,
                    'error': s.error
                }
                for s in stats if not s.success
            ]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def query_user_stats(user_name: str, period: str = 'daily') -> str:
    """
    查询特定用户的统计数据
    
    Args:
        user_name: 用户名称或账号关键词
        period: 统计周期，'daily'(今日) 或 'monthly'(本月)，默认'daily'
    
    Returns:
        JSON格式的用户统计数据
    """
    try:
        stats = await get_daily_stats() if period == 'daily' else await get_monthly_stats()
        user = find_user_by_name(stats, user_name)
        
        if not user:
            return json.dumps({
                'error': f"未找到用户: {user_name}",
                'availableUsers': [
                    {'name': s.name, 'account': s.account}
                    for s in stats
                ]
            }, ensure_ascii=False, indent=2)
        
        if not user.success:
            return json.dumps({
                'error': f"获取用户 {user.name} 的数据失败",
                'details': user.error
            }, ensure_ascii=False, indent=2)
        
        result = {
            'period': '今日统计' if period == 'daily' else '本月统计',
            'user': {
                'name': user.name,
                'account': user.account,
                'cost': format_cost(user.stats.totalCost),
                'requests': user.stats.requests,
                'tokens': format_tokens(user.stats.allTokens),
                'inputTokens': format_tokens(user.stats.inputTokens),
                'usagePercent': calculate_usage_percentage(user.stats.totalCost, 40) + '%' if period == 'daily' else 'N/A'
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def query_top_users(limit: int = 5, period: str = 'daily') -> str:
    """
    查询使用率（费用）最高的前N名用户
    
    Args:
        limit: 返回的用户数量（1-20），默认5
        period: 统计周期，'daily'(今日) 或 'monthly'(本月)，默认'daily'
    
    Returns:
        JSON格式的Top用户列表
    """
    try:
        limit = max(1, min(limit, 20))  # 限制在1-20之间
        stats = await get_daily_stats() if period == 'daily' else await get_monthly_stats()
        top_users = get_top_users(stats, limit)
        
        result = {
            'period': '今日统计' if period == 'daily' else '本月统计',
            'topCount': limit,
            'users': [
                {
                    'rank': index + 1,
                    'name': user.name,
                    'account': user.account,
                    'cost': format_cost(user.stats.totalCost),
                    'requests': user.stats.requests,
                    'tokens': format_tokens(user.stats.allTokens),
                    'usagePercent': calculate_usage_percentage(user.stats.totalCost, 40) + '%' if period == 'daily' else 'N/A'
                }
                for index, user in enumerate(top_users)
            ]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def compare_users(user1_name: str, user2_name: str, period: str = 'daily') -> str:
    """
    比较两个用户的使用情况
    
    Args:
        user1_name: 第一个用户的名称
        user2_name: 第二个用户的名称
        period: 统计周期，'daily'(今日) 或 'monthly'(本月)，默认'daily'
    
    Returns:
        JSON格式的用户对比数据
    """
    try:
        stats = await get_daily_stats() if period == 'daily' else await get_monthly_stats()
        
        user1 = find_user_by_name(stats, user1_name)
        user2 = find_user_by_name(stats, user2_name)
        
        if not user1 or not user2:
            return json.dumps({
                'error': '未找到指定用户',
                'user1Found': user1 is not None,
                'user2Found': user2 is not None,
                'availableUsers': [
                    {'name': s.name, 'account': s.account}
                    for s in stats
                ]
            }, ensure_ascii=False, indent=2)
        
        comparison = compare_users(user1, user2)
        
        result = {
            'period': '今日统计' if period == 'daily' else '本月统计',
            'comparison': {
                'user1': {
                    'name': user1.name,
                    'account': user1.account,
                    'cost': format_cost(user1.stats.totalCost),
                    'requests': user1.stats.requests,
                    'tokens': format_tokens(user1.stats.allTokens)
                },
                'user2': {
                    'name': user2.name,
                    'account': user2.account,
                    'cost': format_cost(user2.stats.totalCost),
                    'requests': user2.stats.requests,
                    'tokens': format_tokens(user2.stats.allTokens)
                },
                'differences': {
                    'cost': {
                        'diff': format_cost(abs(comparison['cost_diff'])),
                        'percent': f"{comparison['cost_diff_percent']:.1f}%",
                        'higher': user1.name if comparison['cost_diff'] > 0 else user2.name
                    },
                    'requests': {
                        'diff': abs(comparison['requests_diff']),
                        'percent': f"{comparison['requests_diff_percent']:.1f}%",
                        'higher': user1.name if comparison['requests_diff'] > 0 else user2.name
                    },
                    'tokens': {
                        'diff': format_tokens(abs(comparison['tokens_diff'])),
                        'percent': f"{comparison['tokens_diff_percent']:.1f}%",
                        'higher': user1.name if comparison['tokens_diff'] > 0 else user2.name
                    }
                }
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def analyze_usage_trend() -> str:
    """
    分析使用趋势，对比今日和本月的平均使用情况
    
    Returns:
        JSON格式的趋势分析数据
    """
    try:
        daily_stats = await get_daily_stats()
        monthly_stats = await get_monthly_stats()
        
        daily_summary = generate_summary(daily_stats)
        monthly_summary = generate_summary(monthly_stats)
        
        # 计算本月平均每日费用
        current_day = date.today().day
        avg_daily_cost = monthly_summary['total_cost'] / current_day if current_day > 0 else 0
        
        result = {
            'trend': {
                'todayCost': format_cost(daily_summary['total_cost']),
                'monthlyAvgDailyCost': format_cost(avg_daily_cost),
                'todayVsAvg': {
                    'diff': format_cost(abs(daily_summary['total_cost'] - avg_daily_cost)),
                    'percent': f"{((daily_summary['total_cost'] - avg_daily_cost) / avg_daily_cost * 100):.1f}%" if avg_daily_cost > 0 else 'N/A',
                    'status': '高于平均' if daily_summary['total_cost'] > avg_daily_cost else '低于平均'
                }
            },
            'today': {
                'totalCost': format_cost(daily_summary['total_cost']),
                'totalRequests': daily_summary['total_requests'],
                'activeUsers': daily_summary['active_users'],
                'avgCostPerUser': format_cost(daily_summary['avg_cost_per_user'])
            },
            'monthly': {
                'totalCost': format_cost(monthly_summary['total_cost']),
                'totalRequests': monthly_summary['total_requests'],
                'activeUsers': monthly_summary['active_users'],
                'avgCostPerUser': format_cost(monthly_summary['avg_cost_per_user']),
                'daysElapsed': current_day
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def detect_anomalies(threshold: float = 40.0, period: str = 'daily') -> str:
    """
    检测异常使用情况，找出超过指定阈值的账号
    
    Args:
        threshold: 费用阈值（默认$40）
        period: 统计周期，'daily'(今日) 或 'monthly'(本月)，默认'daily'
    
    Returns:
        JSON格式的异常检测结果
    """
    try:
        stats = await get_daily_stats() if period == 'daily' else await get_monthly_stats()
        anomalies = detect_anomalies(stats, threshold)
        
        result = {
            'period': '今日统计' if period == 'daily' else '本月统计',
            'threshold': format_cost(threshold),
            'anomalyCount': len(anomalies),
            'anomalies': [
                {
                    'name': user.name,
                    'account': user.account,
                    'cost': format_cost(user.stats.totalCost),
                    'exceeded': format_cost(user.stats.totalCost - threshold),
                    'exceedPercent': f"{((user.stats.totalCost - threshold) / threshold * 100):.1f}%",
                    'requests': user.stats.requests,
                    'tokens': format_tokens(user.stats.allTokens)
                }
                for user in anomalies
            ],
            'message': '未检测到异常使用情况' if len(anomalies) == 0 else f"发现 {len(anomalies)} 个账号超过阈值"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


@mcp.tool()
async def generate_report(period: str = 'daily') -> str:
    """
    生成完整的使用报告和优化建议
    
    Args:
        period: 统计周期，'daily'(今日) 或 'monthly'(本月)，默认'daily'
    
    Returns:
        JSON格式的完整报告
    """
    try:
        stats = await get_daily_stats() if period == 'daily' else await get_monthly_stats()
        summary = generate_summary(stats)
        top_users = get_top_users(stats, 3)
        anomalies = detect_anomalies(stats, 40)
        
        # 生成建议
        suggestions = []
        
        if anomalies:
            suggestions.append(f"⚠️ 发现 {len(anomalies)} 个账号超出日限额，建议关注使用情况")
        
        if summary['avg_cost_per_user'] > 35:
            suggestions.append('💡 平均使用成本较高，建议优化使用频率或Token数量')
        
        if summary['active_users'] < summary['total_users']:
            inactive_count = summary['total_users'] - summary['active_users']
            suggestions.append(f"📊 有 {inactive_count} 个账号未获取到数据，建议检查配置")
        
        if top_users and top_users[0].stats.totalCost > summary['avg_cost_per_user'] * 2:
            suggestions.append(f"🔝 最高使用者费用是平均值的2倍以上，建议了解使用场景")
        
        result = {
            'reportTitle': f"Claude Code使用{'今日' if period == 'daily' else '本月'}报告",
            'generatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'totalUsers': summary['total_users'],
                'activeUsers': summary['active_users'],
                'totalCost': format_cost(summary['total_cost']),
                'totalRequests': f"{summary['total_requests']:,}",
                'totalTokens': format_tokens(summary['total_tokens']),
                'avgCostPerUser': format_cost(summary['avg_cost_per_user']),
                'avgRequestsPerUser': round(summary['avg_requests_per_user'])
            },
            'topUsers': [
                {
                    'rank': index + 1,
                    'name': user.name,
                    'account': user.account,
                    'cost': format_cost(user.stats.totalCost),
                    'requests': user.stats.requests
                }
                for index, user in enumerate(top_users)
            ],
            'anomalies': [
                {
                    'name': user.name,
                    'cost': format_cost(user.stats.totalCost)
                }
                for user in anomalies
            ],
            'suggestions': suggestions,
            'visualizationTips': [
                '可以使用柱状图展示各用户的费用对比',
                '可以使用饼图展示费用占比分布',
                '可以使用折线图展示每日使用趋势'
            ]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    print('========================================', file=sys.stderr)
    print('Claude Stats MCP Server (Python)', file=sys.stderr)
    print('========================================', file=sys.stderr)
    
    # 从环境变量获取配置
    transport = os.getenv('MCP_TRANSPORT', 'stdio')
    port = int(os.getenv('MCP_PORT', '8000'))
    
    print(f'Transport: {transport}', file=sys.stderr)
    
    if transport == 'http':
        print(f'Port: {port}', file=sys.stderr)
        print(f'URL: http://localhost:{port}/mcp', file=sys.stderr)
        print('========================================\n', file=sys.stderr)
        
        mcp.run(transport='http', port=port)
    else:
        print('Mode: STDIO', file=sys.stderr)
        print('========================================\n', file=sys.stderr)
        
        mcp.run(transport='stdio')


if __name__ == '__main__':
    main()

