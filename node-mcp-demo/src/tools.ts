import { z } from 'zod';
import { loadApiKeys } from './utils/configLoader';
import { getAllKeyStats, KeyStatsResult } from './utils/apiClient';
import {
  formatCost,
  formatTokens,
  getTopUsers,
  findUserByName,
  compareUsers,
  detectAnomalies,
  generateSummary,
  sortByCost,
  calculateUsagePercentage
} from './utils/dataAnalyzer';

// 缓存数据，避免频繁请求API
let dailyStatsCache: KeyStatsResult[] | null = null;
let monthlyStatsCache: KeyStatsResult[] | null = null;
let lastDailyFetch: number = 0;
let lastMonthlyFetch: number = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5分钟缓存

/**
 * 获取今日统计（带缓存）
 */
async function getDailyStats(forceRefresh: boolean = false): Promise<KeyStatsResult[]> {
  const now = Date.now();
  if (!forceRefresh && dailyStatsCache && (now - lastDailyFetch) < CACHE_TTL) {
    return dailyStatsCache;
  }

  const apiKeys = loadApiKeys();
  const stats = await getAllKeyStats(apiKeys, 'daily');
  dailyStatsCache = stats;
  lastDailyFetch = now;
  return stats;
}

/**
 * 获取本月统计（带缓存）
 */
async function getMonthlyStats(forceRefresh: boolean = false): Promise<KeyStatsResult[]> {
  const now = Date.now();
  if (!forceRefresh && monthlyStatsCache && (now - lastMonthlyFetch) < CACHE_TTL) {
    return monthlyStatsCache;
  }

  const apiKeys = loadApiKeys();
  const stats = await getAllKeyStats(apiKeys, 'monthly');
  monthlyStatsCache = stats;
  lastMonthlyFetch = now;
  return stats;
}

/**
 * 工具1: 查询今日统计
 */
export const queryTodayStatsTool = {
  name: 'query_today_stats',
  description: '查询今日所有账号的使用统计，包括费用、请求数、Token数等',
  parameters: z.object({
    forceRefresh: z.boolean().optional().describe('是否强制刷新缓存数据（默认false）')
  }),
  execute: async ({ forceRefresh = false }: { forceRefresh?: boolean }, _context?: any) => {
    try {
      const stats = await getDailyStats(forceRefresh);
      const summary = generateSummary(stats);

      const result = {
        period: '今日统计',
        timestamp: new Date().toISOString(),
        summary: {
          totalUsers: summary.totalUsers,
          activeUsers: summary.activeUsers,
          totalCost: formatCost(summary.totalCost),
          totalRequests: summary.totalRequests.toLocaleString(),
          totalTokens: formatTokens(summary.totalTokens),
          avgCostPerUser: formatCost(summary.avgCostPerUser)
        },
        users: stats.filter(s => s.success).map(s => ({
          name: s.name,
          account: s.account,
          cost: formatCost(s.stats.totalCost),
          requests: s.stats.requests,
          tokens: formatTokens(s.stats.allTokens),
          usagePercent: calculateUsagePercentage(s.stats.totalCost, 40) + '%'
        })),
        failedUsers: stats.filter(s => !s.success).map(s => ({
          name: s.name,
          account: s.account,
          error: s.error
        }))
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

/**
 * 工具2: 查询本月统计
 */
export const queryMonthlyStatsTool = {
  name: 'query_monthly_stats',
  description: '查询本月所有账号的使用统计，包括费用、请求数、Token数等',
  parameters: z.object({
    forceRefresh: z.boolean().optional().describe('是否强制刷新缓存数据（默认false）')
  }),
  execute: async ({ forceRefresh = false }: { forceRefresh?: boolean }, _context?: any) => {
    try {
      const stats = await getMonthlyStats(forceRefresh);
      const summary = generateSummary(stats);

      const result = {
        period: '本月统计',
        timestamp: new Date().toISOString(),
        summary: {
          totalUsers: summary.totalUsers,
          activeUsers: summary.activeUsers,
          totalCost: formatCost(summary.totalCost),
          totalRequests: summary.totalRequests.toLocaleString(),
          totalTokens: formatTokens(summary.totalTokens),
          avgCostPerUser: formatCost(summary.avgCostPerUser)
        },
        users: stats.filter(s => s.success).map(s => ({
          name: s.name,
          account: s.account,
          cost: formatCost(s.stats.totalCost),
          requests: s.stats.requests,
          tokens: formatTokens(s.stats.allTokens)
        })),
        failedUsers: stats.filter(s => !s.success).map(s => ({
          name: s.name,
          account: s.account,
          error: s.error
        }))
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

/**
 * 工具3: 查询特定用户统计
 */
export const queryUserStatsTool = {
  name: 'query_user_stats',
  description: '查询特定用户的统计数据，可以指定查询今日或本月',
  parameters: z.object({
    userName: z.string().describe('用户名称或账号关键词'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期：daily(今日) 或 monthly(本月)')
  }),
  execute: async ({ userName, period = 'daily' }: { userName: string; period?: 'daily' | 'monthly' }, _context?: any) => {
    try {
      const stats = period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const user = findUserByName(stats, userName);

      if (!user) {
        return JSON.stringify({
          error: `未找到用户: ${userName}`,
          availableUsers: stats.map(s => ({ name: s.name, account: s.account }))
        }, null, 2);
      }

      if (!user.success) {
        return JSON.stringify({
          error: `获取用户 ${user.name} 的数据失败`,
          details: user.error
        }, null, 2);
      }

      const result = {
        period: period === 'daily' ? '今日统计' : '本月统计',
        user: {
          name: user.name,
          account: user.account,
          cost: formatCost(user.stats.totalCost),
          requests: user.stats.requests,
          tokens: formatTokens(user.stats.allTokens),
          inputTokens: formatTokens(user.stats.inputTokens),
          usagePercent: period === 'daily' 
            ? calculateUsagePercentage(user.stats.totalCost, 40) + '%'
            : 'N/A'
        }
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

/**
 * 工具4: 查询使用率最高的用户
 */
export const queryTopUsersTool = {
  name: 'query_top_users',
  description: '查询使用率（费用）最高的前N名用户',
  parameters: z.object({
    limit: z.number().min(1).max(20).default(5).describe('返回的用户数量（1-20，默认5）'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期：daily(今日) 或 monthly(本月)')
  }),
  execute: async ({ limit = 5, period = 'daily' }: { limit?: number; period?: 'daily' | 'monthly' }, _context?: any) => {
    try {
      const stats = period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const topUsers = getTopUsers(stats, limit);

      const result = {
        period: period === 'daily' ? '今日统计' : '本月统计',
        topCount: limit,
        users: topUsers.map((user, index) => ({
          rank: index + 1,
          name: user.name,
          account: user.account,
          cost: formatCost(user.stats.totalCost),
          requests: user.stats.requests,
          tokens: formatTokens(user.stats.allTokens),
          usagePercent: period === 'daily'
            ? calculateUsagePercentage(user.stats.totalCost, 40) + '%'
            : 'N/A'
        }))
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

/**
 * 工具5: 比较多个用户
 */
export const compareUsersTool = {
  name: 'compare_users',
  description: '比较两个用户的使用情况，包括费用、请求数、Token数的差异',
  parameters: z.object({
    user1Name: z.string().describe('第一个用户的名称'),
    user2Name: z.string().describe('第二个用户的名称'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期：daily(今日) 或 monthly(本月)')
  }),
  execute: async ({ user1Name, user2Name, period = 'daily' }: { 
    user1Name: string; 
    user2Name: string; 
    period?: 'daily' | 'monthly' 
  }, _context?: any) => {
    try {
      const stats = period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      
      const user1 = findUserByName(stats, user1Name);
      const user2 = findUserByName(stats, user2Name);

      if (!user1 || !user2) {
        return JSON.stringify({
          error: '未找到指定用户',
          user1Found: !!user1,
          user2Found: !!user2,
          availableUsers: stats.map(s => ({ name: s.name, account: s.account }))
        }, null, 2);
      }

      const comparison = compareUsers(user1, user2);

      const result = {
        period: period === 'daily' ? '今日统计' : '本月统计',
        comparison: {
          user1: {
            name: user1.name,
            account: user1.account,
            cost: formatCost(user1.stats.totalCost),
            requests: user1.stats.requests,
            tokens: formatTokens(user1.stats.allTokens)
          },
          user2: {
            name: user2.name,
            account: user2.account,
            cost: formatCost(user2.stats.totalCost),
            requests: user2.stats.requests,
            tokens: formatTokens(user2.stats.allTokens)
          },
          differences: {
            cost: {
              diff: formatCost(Math.abs(comparison.costDiff)),
              percent: comparison.costDiffPercent.toFixed(1) + '%',
              higher: comparison.costDiff > 0 ? user1.name : user2.name
            },
            requests: {
              diff: Math.abs(comparison.requestsDiff),
              percent: comparison.requestsDiffPercent.toFixed(1) + '%',
              higher: comparison.requestsDiff > 0 ? user1.name : user2.name
            },
            tokens: {
              diff: formatTokens(Math.abs(comparison.tokensDiff)),
              percent: comparison.tokensDiffPercent.toFixed(1) + '%',
              higher: comparison.tokensDiff > 0 ? user1.name : user2.name
            }
          }
        }
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

/**
 * 工具6: 获取使用趋势
 */
export const getUsageTrendTool = {
  name: 'get_usage_trend',
  description: '获取使用趋势分析，对比今日和本月的平均使用情况',
  parameters: z.object({}),
  execute: async (_args?: any, _context?: any) => {
    try {
      const dailyStats = await getDailyStats();
      const monthlyStats = await getMonthlyStats();

      const dailySummary = generateSummary(dailyStats);
      const monthlySummary = generateSummary(monthlyStats);

      // 计算本月平均每日费用
      const currentDay = new Date().getDate();
      const avgDailyCost = currentDay > 0 ? monthlySummary.totalCost / currentDay : 0;

      const result = {
        trend: {
          todayCost: formatCost(dailySummary.totalCost),
          monthlyAvgDailyCost: formatCost(avgDailyCost),
          todayVsAvg: {
            diff: formatCost(Math.abs(dailySummary.totalCost - avgDailyCost)),
            percent: avgDailyCost > 0 
              ? ((dailySummary.totalCost - avgDailyCost) / avgDailyCost * 100).toFixed(1) + '%'
              : 'N/A',
            status: dailySummary.totalCost > avgDailyCost ? '高于平均' : '低于平均'
          }
        },
        today: {
          totalCost: formatCost(dailySummary.totalCost),
          totalRequests: dailySummary.totalRequests,
          activeUsers: dailySummary.activeUsers,
          avgCostPerUser: formatCost(dailySummary.avgCostPerUser)
        },
        monthly: {
          totalCost: formatCost(monthlySummary.totalCost),
          totalRequests: monthlySummary.totalRequests,
          activeUsers: monthlySummary.activeUsers,
          avgCostPerUser: formatCost(monthlySummary.avgCostPerUser),
          daysElapsed: currentDay
        }
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

/**
 * 工具7: 检测异常使用
 */
export const detectAnomaliesTo = {
  name: 'detect_anomalies',
  description: '检测异常使用情况，找出超过指定阈值的账号',
  parameters: z.object({
    threshold: z.number().min(0).default(40).describe('费用阈值（默认$40）'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期：daily(今日) 或 monthly(本月)')
  }),
  execute: async ({ threshold = 40, period = 'daily' }: { threshold?: number; period?: 'daily' | 'monthly' }, _context?: any) => {
    try {
      const stats = period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const anomalies = detectAnomalies(stats, threshold);

      const result = {
        period: period === 'daily' ? '今日统计' : '本月统计',
        threshold: formatCost(threshold),
        anomalyCount: anomalies.length,
        anomalies: anomalies.map(user => ({
          name: user.name,
          account: user.account,
          cost: formatCost(user.stats.totalCost),
          exceeded: formatCost(user.stats.totalCost - threshold),
          exceedPercent: ((user.stats.totalCost - threshold) / threshold * 100).toFixed(1) + '%',
          requests: user.stats.requests,
          tokens: formatTokens(user.stats.allTokens)
        })),
        message: anomalies.length === 0 
          ? '未检测到异常使用情况' 
          : `发现 ${anomalies.length} 个账号超过阈值`
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

/**
 * 工具8: 生成报告建议
 */
export const generateReportTool = {
  name: 'generate_report',
  description: '生成完整的使用报告和优化建议',
  parameters: z.object({
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期：daily(今日) 或 monthly(本月)')
  }),
  execute: async ({ period = 'daily' }: { period?: 'daily' | 'monthly' }, _context?: any) => {
    try {
      const stats = period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const summary = generateSummary(stats);
      const topUsers = getTopUsers(stats, 3);
      const anomalies = detectAnomalies(stats, 40);

      // 生成建议
      const suggestions: string[] = [];
      
      if (anomalies.length > 0) {
        suggestions.push(`⚠️ 发现 ${anomalies.length} 个账号超出日限额，建议关注使用情况`);
      }

      if (summary.avgCostPerUser > 35) {
        suggestions.push('💡 平均使用成本较高，建议优化使用频率或Token数量');
      }

      if (summary.activeUsers < summary.totalUsers) {
        const inactiveCount = summary.totalUsers - summary.activeUsers;
        suggestions.push(`📊 有 ${inactiveCount} 个账号未获取到数据，建议检查配置`);
      }

      if (topUsers.length > 0 && topUsers[0].stats.totalCost > summary.avgCostPerUser * 2) {
        suggestions.push(`🔝 最高使用者费用是平均值的2倍以上，建议了解使用场景`);
      }

      const result = {
        reportTitle: `Claude Code使用${period === 'daily' ? '今日' : '本月'}报告`,
        generatedAt: new Date().toLocaleString('zh-CN'),
        summary: {
          totalUsers: summary.totalUsers,
          activeUsers: summary.activeUsers,
          totalCost: formatCost(summary.totalCost),
          totalRequests: summary.totalRequests.toLocaleString(),
          totalTokens: formatTokens(summary.totalTokens),
          avgCostPerUser: formatCost(summary.avgCostPerUser),
          avgRequestsPerUser: Math.round(summary.avgRequestsPerUser)
        },
        topUsers: topUsers.map((user, index) => ({
          rank: index + 1,
          name: user.name,
          account: user.account,
          cost: formatCost(user.stats.totalCost),
          requests: user.stats.requests
        })),
        anomalies: anomalies.map(user => ({
          name: user.name,
          cost: formatCost(user.stats.totalCost)
        })),
        suggestions,
        visualizationTips: [
          '可以使用柱状图展示各用户的费用对比',
          '可以使用饼图展示费用占比分布',
          '可以使用折线图展示每日使用趋势'
        ]
      };

      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
};

export const allTools = [
  queryTodayStatsTool,
  queryMonthlyStatsTool,
  queryUserStatsTool,
  queryTopUsersTool,
  compareUsersTool,
  getUsageTrendTool,
  detectAnomaliesTo,
  generateReportTool
];

