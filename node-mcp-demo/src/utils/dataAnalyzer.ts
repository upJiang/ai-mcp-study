import { KeyStatsResult, AggregatedStats } from './apiClient';

/**
 * 计算两个日期之间的工作日数量（排除周六日）
 */
export function getWorkdaysCount(startDate: Date, endDate: Date): number {
  let count = 0;
  const current = new Date(startDate);

  while (current <= endDate) {
    const dayOfWeek = current.getDay();
    // 0 = Sunday, 6 = Saturday
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      count++;
    }
    current.setDate(current.getDate() + 1);
  }

  return count;
}

/**
 * 格式化Token数量
 */
export function formatTokens(tokens: number): string {
  if (tokens >= 1000000) {
    return `${(tokens / 1000000).toFixed(1)}M`;
  } else if (tokens >= 1000) {
    return `${(tokens / 1000).toFixed(1)}K`;
  }
  return tokens.toString();
}

/**
 * 格式化费用
 */
export function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`;
}

/**
 * 按费用排序
 */
export function sortByCost(stats: KeyStatsResult[], descending: boolean = true): KeyStatsResult[] {
  const sorted = [...stats].sort((a, b) => {
    return b.stats.totalCost - a.stats.totalCost;
  });
  return descending ? sorted : sorted.reverse();
}

/**
 * 按请求数排序
 */
export function sortByRequests(stats: KeyStatsResult[], descending: boolean = true): KeyStatsResult[] {
  const sorted = [...stats].sort((a, b) => {
    return b.stats.requests - a.stats.requests;
  });
  return descending ? sorted : sorted.reverse();
}

/**
 * 查找特定用户
 */
export function findUserByName(stats: KeyStatsResult[], userName: string): KeyStatsResult | undefined {
  return stats.find(s => 
    s.name.toLowerCase().includes(userName.toLowerCase()) ||
    s.account.toLowerCase().includes(userName.toLowerCase())
  );
}

/**
 * 获取Top N用户
 */
export function getTopUsers(stats: KeyStatsResult[], limit: number = 5): KeyStatsResult[] {
  return sortByCost(stats).slice(0, limit);
}

/**
 * 计算总计
 */
export function calculateTotals(stats: KeyStatsResult[]): AggregatedStats {
  return stats.reduce((acc, key) => {
    if (key.success) {
      acc.requests += key.stats.requests;
      acc.allTokens += key.stats.allTokens;
      acc.totalCost += key.stats.totalCost;
      acc.inputTokens += key.stats.inputTokens;
    }
    return acc;
  }, {
    requests: 0,
    allTokens: 0,
    totalCost: 0,
    inputTokens: 0
  });
}

/**
 * 检测异常使用（超过日限额）
 */
export function detectAnomalies(stats: KeyStatsResult[], dailyLimit: number = 40): KeyStatsResult[] {
  return stats.filter(s => s.success && s.stats.totalCost > dailyLimit);
}

/**
 * 生成使用率百分比
 */
export function calculateUsagePercentage(cost: number, limit: number): string {
  return ((cost / limit) * 100).toFixed(1);
}

/**
 * 比较两个用户的统计数据
 */
export interface UserComparison {
  user1: KeyStatsResult;
  user2: KeyStatsResult;
  costDiff: number;
  costDiffPercent: number;
  requestsDiff: number;
  requestsDiffPercent: number;
  tokensDiff: number;
  tokensDiffPercent: number;
}

export function compareUsers(user1: KeyStatsResult, user2: KeyStatsResult): UserComparison {
  const costDiff = user1.stats.totalCost - user2.stats.totalCost;
  const costDiffPercent = user2.stats.totalCost > 0 
    ? (costDiff / user2.stats.totalCost) * 100 
    : 0;

  const requestsDiff = user1.stats.requests - user2.stats.requests;
  const requestsDiffPercent = user2.stats.requests > 0
    ? (requestsDiff / user2.stats.requests) * 100
    : 0;

  const tokensDiff = user1.stats.allTokens - user2.stats.allTokens;
  const tokensDiffPercent = user2.stats.allTokens > 0
    ? (tokensDiff / user2.stats.allTokens) * 100
    : 0;

  return {
    user1,
    user2,
    costDiff,
    costDiffPercent,
    requestsDiff,
    requestsDiffPercent,
    tokensDiff,
    tokensDiffPercent
  };
}

/**
 * 生成统计摘要
 */
export interface StatsSummary {
  totalUsers: number;
  activeUsers: number;
  totalCost: number;
  totalRequests: number;
  totalTokens: number;
  avgCostPerUser: number;
  avgRequestsPerUser: number;
  topUser: KeyStatsResult | null;
  anomalies: KeyStatsResult[];
}

export function generateSummary(stats: KeyStatsResult[], dailyLimit: number = 40): StatsSummary {
  const activeStats = stats.filter(s => s.success);
  const totals = calculateTotals(stats);
  const topUsers = getTopUsers(stats, 1);
  const anomalies = detectAnomalies(stats, dailyLimit);

  return {
    totalUsers: stats.length,
    activeUsers: activeStats.length,
    totalCost: totals.totalCost,
    totalRequests: totals.requests,
    totalTokens: totals.allTokens,
    avgCostPerUser: activeStats.length > 0 ? totals.totalCost / activeStats.length : 0,
    avgRequestsPerUser: activeStats.length > 0 ? totals.requests / activeStats.length : 0,
    topUser: topUsers.length > 0 ? topUsers[0] : null,
    anomalies
  };
}

