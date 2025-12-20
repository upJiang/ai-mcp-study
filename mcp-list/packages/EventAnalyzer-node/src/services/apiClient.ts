/**
 * 埋点事件 API 客户端
 * 负责调用 API 获取事件字段定义
 */

import axios, { AxiosInstance } from 'axios';
import NodeCache from 'node-cache';

export interface FieldDefinition {
  type: string;
  desc: string;
  trans?: string;
  required?: boolean;
  enum_values?: Record<string, string>;
}

export interface FieldDefinitions {
  [fieldName: string]: FieldDefinition;
}

export class EventAPIClient {
  private baseUrl: string;
  private cache: NodeCache;
  private axiosInstance: AxiosInstance;

  constructor() {
    // 从环境变量获取 API 地址
    this.baseUrl = process.env.EVENT_API_BASE_URL || 'https://tptest-3d66.top/trans/api/event';

    // 初始化缓存（TTL 1 小时）
    this.cache = new NodeCache({ stdTTL: 3600 });

    // 初始化 axios 实例
    this.axiosInstance = axios.create({
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * 获取事件字段定义
   * @param eventName 事件名称
   */
  async getEventFields(eventName: string): Promise<FieldDefinitions> {
    // 检查缓存
    const cacheKey = `event:${eventName}`;
    const cached = this.cache.get<FieldDefinitions>(cacheKey);
    if (cached) {
      return cached;
    }

    try {
      // 调用 API
      const response = await this.axiosInstance.get(this.baseUrl, {
        params: { event: eventName },
      });

      const fields: FieldDefinitions = response.data;

      // 缓存结果
      this.cache.set(cacheKey, fields);

      return fields;
    } catch (error: any) {
      throw new Error(`获取事件字段定义失败: ${error.message}`);
    }
  }

  /**
   * 解析字段的枚举值字符串
   * @param transStr 枚举值字符串，格式：0:未知,1:成功,2:失败
   * @returns 枚举值映射对象 { "0": "未知", "1": "成功", "2": "失败" }
   */
  parseFieldTrans(transStr: string): Record<string, string> {
    if (!transStr) {
      return {};
    }

    const result: Record<string, string> = {};

    try {
      // 分割枚举项
      const items = transStr.split(',');
      for (const item of items) {
        const [key, value] = item.split(':');
        if (key && value) {
          result[key.trim()] = value.trim();
        }
      }
    } catch {
      // 解析失败，返回空对象
    }

    return result;
  }

  /**
   * 获取单个字段的信息
   * @param eventName 事件名称
   * @param fieldName 字段名称
   */
  async getFieldInfo(eventName: string, fieldName: string): Promise<FieldDefinition | null> {
    const fields = await this.getEventFields(eventName);
    return fields[fieldName] || null;
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    this.cache.flushAll();
  }

  /**
   * 清除特定事件的缓存
   */
  clearEventCache(eventName: string): void {
    this.cache.del(`event:${eventName}`);
  }
}
