#!/usr/bin/env node
/**
 * EventAnalyzer MCP Server (Node.js 版本)
 * 埋点分析 MCP 服务
 *
 * 提供 5 个 Tools:
 * 1. query_event_fields - 查询事件字段定义
 * 2. analyze_tracking_data - 分析埋点数据
 * 3. explain_field - 解释字段含义
 * 4. find_field_in_code - 在代码中搜索字段
 * 5. compare_events - 比较事件差异
 */

import { FastMCP } from 'fastmcp';
import { queryEventFieldsTool } from './tools/queryEventFields.js';
import { analyzeTrackingDataTool } from './tools/analyzeTrackingData.js';
import { explainFieldTool } from './tools/explainField.js';
import { findFieldInCodeTool } from './tools/findFieldInCode.js';
import { compareEventsTool } from './tools/compareEvents.js';

// 创建 FastMCP 服务器实例
const server = new FastMCP({
  name: 'eventanalyzer-node',
  version: '1.0.0',
});

// 注册 5 个 Tools
server.addTool(queryEventFieldsTool);
server.addTool(analyzeTrackingDataTool);
server.addTool(explainFieldTool);
server.addTool(findFieldInCodeTool);
server.addTool(compareEventsTool);

// 启动 stdio 模式
server.start({ transportType: 'stdio' });
