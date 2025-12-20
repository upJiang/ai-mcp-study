/**
 * Tool: analyze_tracking_data
 * 分析埋点数据，检测字段类型错误、缺失字段、枚举值错误等问题
 */

import { z } from 'zod';
import { EventAPIClient } from '../services/apiClient.js';
import { EventAnalyzer } from '../services/eventAnalyzer.js';
import { Base64Decoder } from '../utils/base64Decoder.js';

const apiClient = new EventAPIClient();
const eventAnalyzer = new EventAnalyzer();

export const analyzeTrackingDataSchema = z.object({
  event: z.string().optional().describe('事件名称（可选，从数据中自动提取）'),
  data: z.string().describe('Base64 编码的埋点数据或 JSON 字符串'),
  check_required: z.boolean().optional().default(false).describe('是否检查必填字段（默认 false）'),
});

export type AnalyzeTrackingDataArgs = z.infer<typeof analyzeTrackingDataSchema>;

export async function analyzeTrackingDataHandler(args: AnalyzeTrackingDataArgs): Promise<string> {
  try {
    const { event: eventName, data, check_required } = args;

    // 解码数据
    let eventData: any;
    try {
      eventData = Base64Decoder.decodeFlexible(data);
    } catch (error: any) {
      return JSON.stringify({
        error: `数据解码失败: ${error.message}`,
        tool: 'analyze_tracking_data',
      }, null, 2);
    }

    // 确定事件名称
    const actualEventName = eventName || eventData.event;
    if (!actualEventName) {
      return JSON.stringify({
        error: '无法确定事件名称，请指定 event 参数或确保数据中包含 event 字段',
        tool: 'analyze_tracking_data',
      }, null, 2);
    }

    // 获取字段定义
    const fieldDefinitions = await apiClient.getEventFields(actualEventName);

    // 分析数据
    const result = eventAnalyzer.analyze(eventData, fieldDefinitions, check_required);

    return JSON.stringify(result, null, 2);
  } catch (error: any) {
    return JSON.stringify({
      error: error.message,
      tool: 'analyze_tracking_data',
      arguments: args,
    }, null, 2);
  }
}

export const analyzeTrackingDataTool = {
  name: 'analyze_tracking_data',
  description: '分析埋点数据，检测字段类型错误、缺失字段、枚举值错误等问题',
  parameters: analyzeTrackingDataSchema,
  execute: analyzeTrackingDataHandler,
};
