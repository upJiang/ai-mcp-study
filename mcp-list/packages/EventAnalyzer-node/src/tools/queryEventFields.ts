/**
 * Tool: query_event_fields
 * 查询埋点事件的所有字段定义
 */

import { z } from 'zod';
import { EventAPIClient } from '../services/apiClient.js';

const apiClient = new EventAPIClient();

export const queryEventFieldsSchema = z.object({
  event: z.string().describe('事件名称，如 LlwResExposure、LlwResDownBtnClick'),
  show_details: z.boolean().optional().default(true).describe('是否显示详细信息（默认 true）'),
});

export type QueryEventFieldsArgs = z.infer<typeof queryEventFieldsSchema>;

export async function queryEventFieldsHandler(args: QueryEventFieldsArgs): Promise<string> {
  try {
    const { event, show_details } = args;

    // 获取字段定义
    const fields = await apiClient.getEventFields(event);

    // 如果需要详细信息，解析枚举值
    if (show_details) {
      for (const fieldName in fields) {
        const fieldDef = fields[fieldName];
        if (fieldDef.trans) {
          fieldDef.enum_values = apiClient.parseFieldTrans(fieldDef.trans);
        }
      }
    }

    const result = {
      event,
      total_fields: Object.keys(fields).length,
      fields,
    };

    return JSON.stringify(result, null, 2);
  } catch (error: any) {
    return JSON.stringify({
      error: error.message,
      tool: 'query_event_fields',
      arguments: args,
    }, null, 2);
  }
}

export const queryEventFieldsTool = {
  name: 'query_event_fields',
  description: '查询埋点事件的所有字段定义，返回字段类型、说明、枚举值等信息',
  parameters: queryEventFieldsSchema,
  execute: queryEventFieldsHandler,
};
