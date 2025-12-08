import httpx
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

API_BASE_URL = os.getenv('API_BASE_URL', 'https://as.imds.ai/apiStats/api')


@dataclass
class ApiKeyInfo:
    """API Key信息"""
    name: str
    account: str
    apiKey: str


@dataclass
class AggregatedStats:
    """汇总统计数据"""
    requests: int = 0
    allTokens: int = 0
    totalCost: float = 0.0
    inputTokens: int = 0


@dataclass
class KeyStatsResult:
    """单个Key的统计结果"""
    name: str
    account: str
    apiKey: str
    stats: AggregatedStats
    success: bool
    error: Optional[str] = None


async def get_api_id(api_key: str) -> str:
    """获取apiId"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/get-key-id",
                json={"apiKey": api_key},
                timeout=10.0
            )
            data = response.json()
            
            if data and data.get('success'):
                api_id = data['data'].get('id') or data['data']
                return api_id
            
            raise Exception(f"获取apiId失败: {data}")
    except Exception as e:
        raise Exception(f"获取apiId失败 ({api_key}): {str(e)}")


async def fetch_stats(api_id: str, period: str) -> Dict[str, Any]:
    """获取统计数据"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/user-model-stats",
                json={"apiId": api_id, "period": period},
                timeout=10.0
            )
            data = response.json()
            
            if data and data.get('success'):
                return data
            
            raise Exception(f"获取统计数据失败: {data}")
    except Exception as e:
        raise Exception(f"获取统计数据失败 (apiId: {api_id}, period: {period}): {str(e)}")


def aggregate_data(model_data: List[Dict[str, Any]]) -> AggregatedStats:
    """汇总所有模型的数据"""
    if not model_data:
        return AggregatedStats()
    
    aggregated = AggregatedStats()
    
    for model in model_data:
        aggregated.requests += model.get('requests', 0)
        aggregated.allTokens += model.get('allTokens', 0)
        aggregated.totalCost += model.get('costs', {}).get('total', 0)
        aggregated.inputTokens += model.get('inputTokens', 0)
    
    return aggregated


async def get_key_stats(
    key_info: ApiKeyInfo,
    period: str,
    retries: int = 3
) -> KeyStatsResult:
    """获取单个Key的统计数据（含重试机制）"""
    last_error = None
    
    for i in range(retries):
        try:
            # 步骤1：获取apiId
            api_id = await get_api_id(key_info.apiKey)
            
            # 步骤2：获取统计数据
            stats = await fetch_stats(api_id, period)
            
            # 步骤3：汇总数据
            aggregated = aggregate_data(stats.get('data', []))
            
            return KeyStatsResult(
                name=key_info.name,
                account=key_info.account,
                apiKey=key_info.apiKey,
                stats=aggregated,
                success=True
            )
        except Exception as e:
            last_error = e
            print(f"尝试 {i + 1}/{retries} 失败: {str(e)}")
            
            # 如果不是最后一次重试，等待1秒后重试
            if i < retries - 1:
                import asyncio
                await asyncio.sleep(1)
    
    # 所有重试都失败
    print(f"获取 {key_info.name} ({key_info.account}) 的统计数据失败: {str(last_error)}")
    return KeyStatsResult(
        name=key_info.name,
        account=key_info.account,
        apiKey=key_info.apiKey,
        stats=AggregatedStats(),
        success=False,
        error=str(last_error)
    )


async def get_all_key_stats(
    api_keys: List[ApiKeyInfo],
    period: str
) -> List[KeyStatsResult]:
    """批量获取所有Key的统计数据"""
    import asyncio
    
    print(f"开始获取所有Key的{'今日' if period == 'daily' else '本月'}统计数据...")
    
    # 并发请求所有Key的数据
    tasks = [get_key_stats(key_info, period) for key_info in api_keys]
    results = await asyncio.gather(*tasks)
    
    # 统计成功和失败的数量
    success_count = sum(1 for r in results if r.success)
    fail_count = sum(1 for r in results if not r.success)
    
    print(f"统计完成: {success_count} 成功, {fail_count} 失败")
    
    return list(results)

