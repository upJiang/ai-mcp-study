#!/usr/bin/env node

import { FastMCP } from 'fastmcp';
import { z } from 'zod';
import * as dotenv from 'dotenv';
import { loadApiKeys } from './utils/configLoader.js';
import { getAllKeyStats } from './utils/apiClient.js';
import {
  formatCost,
  formatTokens,
  getTopUsers,
  findUserByName,
  compareUsers,
  detectAnomalies,
  generateSummary,
  calculateUsagePercentage
} from './utils/dataAnalyzer.js';

// 加载环境变量
dotenv.config();

// 创建FastMCP服务器实例
const server = new FastMCP({
  name: 'Claude Stats MCP',
  version: '1.0.0',
});

// 缓存数据
let dailyStatsCache: any = null;
let monthlyStatsCache: any = null;
let lastDailyFetch = 0;
let lastMonthlyFetch = 0;
const CACHE_TTL = 5 * 60 * 1000;

async function getDailyStats(forceRefresh = false) {
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

async function getMonthlyStats(forceRefresh = false) {
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

// 工具1: 查询今日统计
server.addTool({
  name: 'query_today_stats',
  description: '查询今日所有账号的使用统计，包括费用、请求数、Token数等',
  parameters: z.object({
    forceRefresh: z.boolean().optional().describe('是否强制刷新缓存数据（默认false）')
  }),
  execute: async (args) => {
    try {
      const stats = await getDailyStats(args.forceRefresh);
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
        users: stats.filter((s: any) => s.success).map((s: any) => ({
          name: s.name,
          account: s.account,
          cost: formatCost(s.stats.totalCost),
          requests: s.stats.requests,
          tokens: formatTokens(s.stats.allTokens),
          usagePercent: calculateUsagePercentage(s.stats.totalCost, 40) + '%'
        }))
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 工具2: 查询本月统计
server.addTool({
  name: 'query_monthly_stats',
  description: '查询本月所有账号的使用统计，包括费用、请求数、Token数等',
  parameters: z.object({
    forceRefresh: z.boolean().optional().describe('是否强制刷新缓存数据（默认false）')
  }),
  execute: async (args) => {
    try {
      const stats = await getMonthlyStats(args.forceRefresh);
      const summary = generateSummary(stats);
      const result = {
        period: '本月统计',
        timestamp: new Date().toISOString(),
        summary: {
          totalUsers: summary.totalUsers,
          activeUsers: summary.activeUsers,
          totalCost: formatCost(summary.totalCost),
          totalRequests: summary.totalRequests.toLocaleString(),
          totalTokens: formatTokens(summary.totalTokens)
        },
        users: stats.filter((s: any) => s.success).map((s: any) => ({
          name: s.name,
          account: s.account,
          cost: formatCost(s.stats.totalCost),
          requests: s.stats.requests,
          tokens: formatTokens(s.stats.allTokens)
        }))
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 工具3: 查询特定用户
server.addTool({
  name: 'query_user_stats',
  description: '查询特定用户的统计数据，可以指定查询今日或本月',
  parameters: z.object({
    userName: z.string().describe('用户名称或账号关键词'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期：daily(今日) 或 monthly(本月)')
  }),
  execute: async (args) => {
    try {
      const stats = args.period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const user = findUserByName(stats, args.userName);
      if (!user) {
        return JSON.stringify({ error: `未找到用户: ${args.userName}` }, null, 2);
      }
      const result = {
        period: args.period === 'daily' ? '今日统计' : '本月统计',
        user: {
          name: user.name,
          account: user.account,
          cost: formatCost(user.stats.totalCost),
          requests: user.stats.requests,
          tokens: formatTokens(user.stats.allTokens)
        }
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 工具4: Top用户
server.addTool({
  name: 'query_top_users',
  description: '查询使用率最高的前N名用户',
  parameters: z.object({
    limit: z.number().min(1).max(20).default(5).describe('返回数量（1-20）'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期')
  }),
  execute: async (args) => {
    try {
      const stats = args.period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const topUsers = getTopUsers(stats, args.limit);
      const result = {
        period: args.period === 'daily' ? '今日统计' : '本月统计',
        users: topUsers.map((u: any, i: number) => ({
          rank: i + 1,
          name: u.name,
          cost: formatCost(u.stats.totalCost),
          requests: u.stats.requests
        }))
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 工具5: 比较用户
server.addTool({
  name: 'compare_users',
  description: '比较两个用户的使用情况',
  parameters: z.object({
    user1Name: z.string().describe('第一个用户'),
    user2Name: z.string().describe('第二个用户'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期')
  }),
  execute: async (args) => {
    try {
      const stats = args.period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const user1 = findUserByName(stats, args.user1Name);
      const user2 = findUserByName(stats, args.user2Name);
      if (!user1 || !user2) {
        return JSON.stringify({ error: '未找到用户' }, null, 2);
      }
      const comparison = compareUsers(user1, user2);
      const result = {
        user1: { name: user1.name, cost: formatCost(user1.stats.totalCost) },
        user2: { name: user2.name, cost: formatCost(user2.stats.totalCost) },
        diff: formatCost(Math.abs(comparison.costDiff))
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 工具6: 趋势分析
server.addTool({
  name: 'get_usage_trend',
  description: '获取使用趋势分析',
  parameters: z.object({}),
  execute: async () => {
    try {
      const dailyStats = await getDailyStats();
      const monthlyStats = await getMonthlyStats();
      const dailySummary = generateSummary(dailyStats);
      const monthlySummary = generateSummary(monthlyStats);
      const result = {
        today: formatCost(dailySummary.totalCost),
        monthly: formatCost(monthlySummary.totalCost)
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 工具7: 异常检测
server.addTool({
  name: 'detect_anomalies',
  description: '检测异常使用情况',
  parameters: z.object({
    threshold: z.number().default(40).describe('费用阈值'),
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期')
  }),
  execute: async (args) => {
    try {
      const stats = args.period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const anomalies = detectAnomalies(stats, args.threshold);
      const result = {
        anomalyCount: anomalies.length,
        anomalies: anomalies.map((u: any) => ({
          name: u.name,
          cost: formatCost(u.stats.totalCost)
        }))
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 工具8: 生成报告
server.addTool({
  name: 'generate_report',
  description: '生成完整的使用报告',
  parameters: z.object({
    period: z.enum(['daily', 'monthly']).default('daily').describe('统计周期')
  }),
  execute: async (args) => {
    try {
      const stats = args.period === 'daily' ? await getDailyStats() : await getMonthlyStats();
      const summary = generateSummary(stats);
      const topUsers = getTopUsers(stats, 3);
      const result = {
        reportTitle: `Claude Code使用${args.period === 'daily' ? '今日' : '本月'}报告`,
        summary: {
          totalCost: formatCost(summary.totalCost),
          totalRequests: summary.totalRequests
        },
        topUsers: topUsers.map((u: any, i: number) => ({
          rank: i + 1,
          name: u.name,
          cost: formatCost(u.stats.totalCost)
        }))
      };
      return JSON.stringify(result, null, 2);
    } catch (error: any) {
      return JSON.stringify({ error: error.message }, null, 2);
    }
  }
});

// 从环境变量获取传输模式
const transport = process.env.MCP_TRANSPORT || 'stdio';
const port = parseInt(process.env.MCP_PORT || '8000', 10);

console.error('========================================');
console.error('Claude Stats MCP Server');
console.error('========================================');
console.error(`Transport: ${transport.toUpperCase()}`);

if (transport === 'http' || transport === 'httpStream') {
  console.error(`Port: ${port}`);
  console.error(`URL: http://localhost:${port}/mcp`);
  console.error('========================================\n');
  
  server.start({
    transportType: 'httpStream',
    httpStream: {
      port
    }
  });
} else {
  console.error('Mode: STDIO');
  console.error('========================================\n');
  
  server.start({
    transportType: 'stdio'
  });
}
