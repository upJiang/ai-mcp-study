/**
 * 字段解释器
 * 解释字段含义并搜索相关字段
 */

import { FieldDefinition, FieldDefinitions } from './apiClient.js';

export interface ExplanationResult {
  field_name: string;
  type: string;
  description: string;
  required: boolean;
  enum_values?: Record<string, string>;
  related_fields?: string[];
}

export class FieldExplainer {
  /**
   * 解释字段含义
   * @param fieldName 字段名称
   * @param fieldInfo 字段信息
   * @param showEnum 是否显示枚举值
   */
  explainField(fieldName: string, fieldInfo: FieldDefinition, showEnum: boolean = true): ExplanationResult {
    const result: ExplanationResult = {
      field_name: fieldName,
      type: fieldInfo.type,
      description: fieldInfo.desc || '无描述',
      required: fieldInfo.required || false,
    };

    // 解析枚举值
    if (showEnum && fieldInfo.trans) {
      result.enum_values = this.parseEnumValues(fieldInfo.trans);
    }

    return result;
  }

  /**
   * 搜索相关字段
   * 基于字段名称的相似度，返回相关字段列表
   * @param fieldName 目标字段名称
   * @param allFields 所有字段定义
   * @param maxResults 最大返回数量
   */
  searchRelatedFields(
    fieldName: string,
    allFields: FieldDefinitions,
    maxResults: number = 5
  ): string[] {
    const related: Array<{ field: string; score: number }> = [];

    for (const otherField in allFields) {
      if (otherField === fieldName) {
        continue;
      }

      const score = this.calculateSimilarity(fieldName, otherField);
      if (score > 0) {
        related.push({ field: otherField, score });
      }
    }

    // 按相似度排序
    related.sort((a, b) => b.score - a.score);

    // 返回前 N 个
    return related.slice(0, maxResults).map((item) => item.field);
  }

  /**
   * 计算两个字符串的相似度
   * 基于共同子串和长度
   */
  private calculateSimilarity(str1: string, str2: string): number {
    const s1 = str1.toLowerCase();
    const s2 = str2.toLowerCase();

    let score = 0;

    // 1. 完全包含关系
    if (s1.includes(s2) || s2.includes(s1)) {
      score += 5;
    }

    // 2. 共同前缀
    const commonPrefix = this.getCommonPrefix(s1, s2);
    if (commonPrefix.length > 2) {
      score += commonPrefix.length;
    }

    // 3. 共同后缀
    const commonSuffix = this.getCommonSuffix(s1, s2);
    if (commonSuffix.length > 2) {
      score += commonSuffix.length;
    }

    // 4. 共同子串
    const commonSubstrings = this.findCommonSubstrings(s1, s2);
    for (const substring of commonSubstrings) {
      if (substring.length > 2) {
        score += substring.length * 0.5;
      }
    }

    return score;
  }

  /**
   * 获取共同前缀
   */
  private getCommonPrefix(str1: string, str2: string): string {
    let i = 0;
    while (i < str1.length && i < str2.length && str1[i] === str2[i]) {
      i++;
    }
    return str1.substring(0, i);
  }

  /**
   * 获取共同后缀
   */
  private getCommonSuffix(str1: string, str2: string): string {
    let i = 0;
    while (
      i < str1.length &&
      i < str2.length &&
      str1[str1.length - 1 - i] === str2[str2.length - 1 - i]
    ) {
      i++;
    }
    return str1.substring(str1.length - i);
  }

  /**
   * 查找共同子串
   */
  private findCommonSubstrings(str1: string, str2: string): string[] {
    const substrings: Set<string> = new Set();

    for (let i = 0; i < str1.length; i++) {
      for (let j = i + 3; j <= str1.length; j++) {
        const substring = str1.substring(i, j);
        if (str2.includes(substring)) {
          substrings.add(substring);
        }
      }
    }

    return Array.from(substrings);
  }

  /**
   * 解析枚举值字符串
   */
  private parseEnumValues(transStr: string): Record<string, string> {
    const result: Record<string, string> = {};

    try {
      const items = transStr.split(',');
      for (const item of items) {
        const [key, value] = item.split(':');
        if (key && value) {
          result[key.trim()] = value.trim();
        }
      }
    } catch {
      // 解析失败
    }

    return result;
  }
}
