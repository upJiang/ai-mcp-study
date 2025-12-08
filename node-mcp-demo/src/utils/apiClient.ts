import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.API_BASE_URL || 'https://as.imds.ai/apiStats/api';

export interface ApiKeyInfo {
  name: string;
  account: string;
  apiKey: string;
}

export interface ModelStats {
  requests: number;
  allTokens: number;
  inputTokens: number;
  costs: {
    total: number;
  };
}

export interface AggregatedStats {
  requests: number;
  allTokens: number;
  totalCost: number;
  inputTokens: number;
}

export interface KeyStatsResult extends ApiKeyInfo {
  stats: AggregatedStats;
  success: boolean;
  error?: string;
}

/**
 * 获取apiId
 */
export async function getApiId(apiKey: string): Promise<string> {
  try {
    const response = await axios.post(`${API_BASE_URL}/get-key-id`, { apiKey });
    if (response.data && response.data.success) {
      const apiId = response.data.data.id || response.data.data;
      return apiId;
    }
    throw new Error(`获取apiId失败: ${JSON.stringify(response.data)}`);
  } catch (error: any) {
    throw new Error(`获取apiId失败 (${apiKey}): ${error.message}`);
  }
}

/**
 * 获取统计数据
 */
export async function fetchStats(apiId: string, period: 'daily' | 'monthly'): Promise<any> {
  try {
    const response = await axios.post(`${API_BASE_URL}/user-model-stats`, {
      apiId,
      period
    });

    if (response.data && response.data.success) {
      return response.data;
    }
    throw new Error(`获取统计数据失败: ${JSON.stringify(response.data)}`);
  } catch (error: any) {
    const errorMsg = error.response?.data
      ? JSON.stringify(error.response.data)
      : error.message;
    throw new Error(`获取统计数据失败 (apiId: ${apiId}, period: ${period}): ${errorMsg}`);
  }
}

/**
 * 汇总所有模型的数据
 */
export function aggregateData(modelData: ModelStats[]): AggregatedStats {
  if (!modelData || modelData.length === 0) {
    return {
      requests: 0,
      allTokens: 0,
      totalCost: 0,
      inputTokens: 0
    };
  }

  const aggregated = modelData.reduce((acc, model) => {
    acc.requests += model.requests || 0;
    acc.allTokens += model.allTokens || 0;
    acc.totalCost += model.costs?.total || 0;
    acc.inputTokens += model.inputTokens || 0;
    return acc;
  }, {
    requests: 0,
    allTokens: 0,
    totalCost: 0,
    inputTokens: 0
  });

  return aggregated;
}

/**
 * 获取单个Key的统计数据（含重试机制）
 */
export async function getKeyStats(
  keyInfo: ApiKeyInfo,
  period: 'daily' | 'monthly',
  retries: number = 3
): Promise<KeyStatsResult> {
  let lastError: Error | undefined;

  for (let i = 0; i < retries; i++) {
    try {
      // 步骤1：获取apiId
      const apiId = await getApiId(keyInfo.apiKey);

      // 步骤2：获取统计数据
      const stats = await fetchStats(apiId, period);

      // 步骤3：汇总数据
      const aggregated = aggregateData(stats.data);

      return {
        ...keyInfo,
        stats: aggregated,
        success: true
      };
    } catch (error: any) {
      lastError = error;
      console.error(`尝试 ${i + 1}/${retries} 失败:`, error.message);

      // 如果不是最后一次重试，等待一秒后重试
      if (i < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }

  // 所有重试都失败
  console.error(`获取 ${keyInfo.name} (${keyInfo.account}) 的统计数据失败:`, lastError?.message);
  return {
    ...keyInfo,
    stats: {
      requests: 0,
      allTokens: 0,
      totalCost: 0,
      inputTokens: 0
    },
    success: false,
    error: lastError?.message
  };
}

/**
 * 批量获取所有Key的统计数据
 */
export async function getAllKeyStats(
  apiKeys: ApiKeyInfo[],
  period: 'daily' | 'monthly'
): Promise<KeyStatsResult[]> {
  console.log(`开始获取所有Key的${period === 'daily' ? '今日' : '本月'}统计数据...`);

  // 并发请求所有Key的数据
  const promises = apiKeys.map(keyInfo => getKeyStats(keyInfo, period));
  const results = await Promise.all(promises);

  // 统计成功和失败的数量
  const successCount = results.filter(r => r.success).length;
  const failCount = results.filter(r => !r.success).length;

  console.log(`统计完成: ${successCount} 成功, ${failCount} 失败`);

  return results;
}

