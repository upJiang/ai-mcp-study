/**
 * Tool: find_field_in_code
 * 在指定项目中搜索字段的实现位置
 */

import { z } from 'zod';
import { CodeSearcher } from '../services/codeSearcher.js';

const codeSearcher = new CodeSearcher();

export const findFieldInCodeSchema = z.object({
  field_name: z.string().describe('字段名称'),
  project_path: z.string().describe('项目根目录的绝对路径'),
  max_results: z.number().optional().default(50).describe('最大结果数（默认 50）'),
});

export type FindFieldInCodeArgs = z.infer<typeof findFieldInCodeSchema>;

export async function findFieldInCodeHandler(args: FindFieldInCodeArgs): Promise<string> {
  try {
    const { field_name, project_path, max_results } = args;

    // 搜索字段
    const result = codeSearcher.findField(field_name, project_path, max_results);

    return JSON.stringify(result, null, 2);
  } catch (error: any) {
    return JSON.stringify({
      error: error.message,
      tool: 'find_field_in_code',
      arguments: args,
    }, null, 2);
  }
}

export const findFieldInCodeTool = {
  name: 'find_field_in_code',
  description: '在指定项目中搜索字段的实现位置',
  parameters: findFieldInCodeSchema,
  execute: findFieldInCodeHandler,
};
