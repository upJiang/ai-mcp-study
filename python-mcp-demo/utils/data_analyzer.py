from typing import List, Optional, Tuple
from datetime import datetime, date
from .api_client import KeyStatsResult, AggregatedStats


def get_workdays_count(start_date: date, end_date: date) -> int:
    """计算两个日期之间的工作日数量（排除周六日）"""
    count = 0
    current = start_date
    
    while current <= end_date:
        # 0 = Monday, 6 = Sunday
        if current.weekday() < 5:  # Monday to Friday
            count += 1
        current = date.fromordinal(current.toordinal() + 1)
    
    return count


def format_tokens(tokens: int) -> str:
    """格式化Token数量"""
    if tokens >= 1000000:
        return f"{tokens / 1000000:.1f}M"
    elif tokens >= 1000:
        return f"{tokens / 1000:.1f}K"
    return str(tokens)


def format_cost(cost: float) -> str:
    """格式化费用"""
    return f"${cost:.2f}"


def sort_by_cost(stats: List[KeyStatsResult], descending: bool = True) -> List[KeyStatsResult]:
    """按费用排序"""
    return sorted(stats, key=lambda x: x.stats.totalCost, reverse=descending)


def sort_by_requests(stats: List[KeyStatsResult], descending: bool = True) -> List[KeyStatsResult]:
    """按请求数排序"""
    return sorted(stats, key=lambda x: x.stats.requests, reverse=descending)


def find_user_by_name(stats: List[KeyStatsResult], user_name: str) -> Optional[KeyStatsResult]:
    """查找特定用户"""
    user_name_lower = user_name.lower()
    for s in stats:
        if user_name_lower in s.name.lower() or user_name_lower in s.account.lower():
            return s
    return None


def get_top_users(stats: List[KeyStatsResult], limit: int = 5) -> List[KeyStatsResult]:
    """获取Top N用户"""
    return sort_by_cost(stats)[:limit]


def calculate_totals(stats: List[KeyStatsResult]) -> AggregatedStats:
    """计算总计"""
    totals = AggregatedStats()
    
    for key in stats:
        if key.success:
            totals.requests += key.stats.requests
            totals.allTokens += key.stats.allTokens
            totals.totalCost += key.stats.totalCost
            totals.inputTokens += key.stats.inputTokens
    
    return totals


def detect_anomalies(stats: List[KeyStatsResult], daily_limit: float = 40.0) -> List[KeyStatsResult]:
    """检测异常使用（超过日限额）"""
    return [s for s in stats if s.success and s.stats.totalCost > daily_limit]


def calculate_usage_percentage(cost: float, limit: float) -> str:
    """生成使用率百分比"""
    return f"{(cost / limit) * 100:.1f}"


def compare_users(user1: KeyStatsResult, user2: KeyStatsResult) -> dict:
    """比较两个用户的统计数据"""
    cost_diff = user1.stats.totalCost - user2.stats.totalCost
    cost_diff_percent = (cost_diff / user2.stats.totalCost * 100) if user2.stats.totalCost > 0 else 0
    
    requests_diff = user1.stats.requests - user2.stats.requests
    requests_diff_percent = (requests_diff / user2.stats.requests * 100) if user2.stats.requests > 0 else 0
    
    tokens_diff = user1.stats.allTokens - user2.stats.allTokens
    tokens_diff_percent = (tokens_diff / user2.stats.allTokens * 100) if user2.stats.allTokens > 0 else 0
    
    return {
        'user1': user1,
        'user2': user2,
        'cost_diff': cost_diff,
        'cost_diff_percent': cost_diff_percent,
        'requests_diff': requests_diff,
        'requests_diff_percent': requests_diff_percent,
        'tokens_diff': tokens_diff,
        'tokens_diff_percent': tokens_diff_percent
    }


def generate_summary(stats: List[KeyStatsResult], daily_limit: float = 40.0) -> dict:
    """生成统计摘要"""
    active_stats = [s for s in stats if s.success]
    totals = calculate_totals(stats)
    top_users = get_top_users(stats, 1)
    anomalies = detect_anomalies(stats, daily_limit)
    
    return {
        'total_users': len(stats),
        'active_users': len(active_stats),
        'total_cost': totals.totalCost,
        'total_requests': totals.requests,
        'total_tokens': totals.allTokens,
        'avg_cost_per_user': totals.totalCost / len(active_stats) if active_stats else 0,
        'avg_requests_per_user': totals.requests / len(active_stats) if active_stats else 0,
        'top_user': top_users[0] if top_users else None,
        'anomalies': anomalies
    }

