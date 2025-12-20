/**
 * Tool: compare_events
 * 比较两个埋点事件的字段差异
 */

import { z } from 'zod';
import { EventAPIClient } from '../services/apiClient.js';
import { EventAnalyzer } from '../services/eventAnalyzer.js';

const apiClient = new EventAPIClient();
const eventAnalyzer = new EventAnalyzer();

export const compareEventsSchema = z.object({
  event1: z.string().describe('第一个事件名称'),
  event2: z.string().describe('第二个事件名称'),
});

export type CompareEventsArgs = z.infer<typeof compareEventsSchema>;

export async function compareEventsHandler(args: CompareEventsArgs): Promise<string> {
  try {
    const { event1, event2 } = args;

    // 获取两个事件的字段定义
    const fields1 = await apiClient.getEventFields(event1);
    const fields2 = await apiClient.getEventFields(event2);

    // 比较事件
    const result = eventAnalyzer.compareEvents(fields1, fields2);
    result.event1 = event1;
    result.event2 = event2;

    return JSON.stringify(result, null, 2);
  } catch (error: any) {
    return JSON.stringify({
      error: error.message,
      tool: 'compare_events',
      arguments: args,
    }, null, 2);
  }
}

export const compareEventsTool = {
  name: 'compare_events',
  description: '比较两个埋点事件的字段差异',
  parameters: compareEventsSchema,
  execute: compareEventsHandler,
};
