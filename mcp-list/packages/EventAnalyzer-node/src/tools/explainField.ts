/**
 * Tool: explain_field
 * 解释埋点字段的含义、类型和枚举值
 */

import { z } from 'zod';
import { EventAPIClient } from '../services/apiClient.js';
import { FieldExplainer } from '../services/fieldExplainer.js';

const apiClient = new EventAPIClient();
const fieldExplainer = new FieldExplainer();

export const explainFieldSchema = z.object({
  event: z.string().describe('事件名称'),
  field_name: z.string().describe('字段名称'),
  show_enum: z.boolean().optional().default(true).describe('是否显示枚举值（默认 true）'),
});

export type ExplainFieldArgs = z.infer<typeof explainFieldSchema>;

export async function explainFieldHandler(args: ExplainFieldArgs): Promise<string> {
  try {
    const { event, field_name, show_enum } = args;

    // 获取字段信息
    const fieldInfo = await apiClient.getFieldInfo(event, field_name);

    if (!fieldInfo) {
      return JSON.stringify({
        error: `字段 ${field_name} 在事件 ${event} 中不存在`,
        tool: 'explain_field',
      }, null, 2);
    }

    // 解释字段
    const result = fieldExplainer.explainField(field_name, fieldInfo, show_enum);

    // 查找相关字段
    const allFields = await apiClient.getEventFields(event);
    const relatedFields = fieldExplainer.searchRelatedFields(field_name, allFields);
    result.related_fields = relatedFields;

    return JSON.stringify(result, null, 2);
  } catch (error: any) {
    return JSON.stringify({
      error: error.message,
      tool: 'explain_field',
      arguments: args,
    }, null, 2);
  }
}

export const explainFieldTool = {
  name: 'explain_field',
  description: '解释埋点字段的含义、类型和枚举值',
  parameters: explainFieldSchema,
  execute: explainFieldHandler,
};
