/**
 * 事件分析器
 * 分析埋点数据，检测类型错误、未知字段、枚举值错误等
 */

import { TypeChecker, TypeName } from '../utils/typeChecker.js';
import { FieldDefinitions, FieldDefinition } from './apiClient.js';

export interface TypeErrorItem {
  field: string;
  expected: string;
  actual: string;
  value: any;
}

export interface EnumErrorItem {
  field: string;
  value: any;
  valid_values: string[];
}

export interface UnknownFieldItem {
  field: string;
  value: any;
}

export interface MissingFieldItem {
  field: string;
  type: string;
}

export interface AnalysisResult {
  event: string;
  total_fields: number;
  analyzed_fields: number;
  type_errors: TypeErrorItem[];
  enum_errors: EnumErrorItem[];
  unknown_fields: UnknownFieldItem[];
  missing_required_fields?: MissingFieldItem[];
  coverage: string;
  summary: string;
}

export interface ComparisonResult {
  event1: string;
  event2: string;
  common_fields: string[];
  only_in_event1: string[];
  only_in_event2: string[];
  type_differences: Array<{
    field: string;
    event1_type: string;
    event2_type: string;
  }>;
}

export class EventAnalyzer {
  /**
   * 分析埋点数据
   * @param eventData 埋点数据
   * @param fieldDefinitions 字段定义
   * @param checkRequired 是否检查必填字段
   */
  analyze(
    eventData: any,
    fieldDefinitions: FieldDefinitions,
    checkRequired: boolean = false
  ): AnalysisResult {
    const eventName = eventData.event || 'Unknown';
    const typeErrors: TypeErrorItem[] = [];
    const enumErrors: EnumErrorItem[] = [];
    const unknownFields: UnknownFieldItem[] = [];
    const missingRequiredFields: MissingFieldItem[] = [];

    // 1. 检查未知字段
    for (const fieldName in eventData) {
      if (!fieldDefinitions[fieldName]) {
        unknownFields.push({
          field: fieldName,
          value: eventData[fieldName],
        });
      }
    }

    // 2. 检查已定义字段
    for (const fieldName in fieldDefinitions) {
      const fieldDef = fieldDefinitions[fieldName];
      const fieldValue = eventData[fieldName];

      // 检查必填字段
      if (checkRequired && fieldDef.required && (fieldValue === undefined || fieldValue === null)) {
        missingRequiredFields.push({
          field: fieldName,
          type: fieldDef.type,
        });
        continue;
      }

      // 如果字段存在，检查类型和枚举值
      if (fieldValue !== undefined && fieldValue !== null) {
        // 类型检查
        const expectedType = this.mapTypeToTypeName(fieldDef.type);
        const actualType = TypeChecker.inferType(fieldValue);

        if (!TypeChecker.typeMatches(expectedType, actualType, fieldValue)) {
          typeErrors.push({
            field: fieldName,
            expected: TypeChecker.getTypeName(expectedType),
            actual: TypeChecker.getTypeName(actualType),
            value: fieldValue,
          });
        }

        // 枚举值检查
        if (fieldDef.trans) {
          const enumValues = this.parseEnumValues(fieldDef.trans);
          if (!TypeChecker.validateEnum(fieldValue, enumValues)) {
            enumErrors.push({
              field: fieldName,
              value: fieldValue,
              valid_values: Object.keys(enumValues),
            });
          }
        }
      }
    }

    // 3. 计算覆盖率
    const totalFields = Object.keys(fieldDefinitions).length;
    const analyzedFields = totalFields - missingRequiredFields.length;
    const coverage = totalFields > 0 ? ((analyzedFields / totalFields) * 100).toFixed(2) : '0.00';

    // 4. 生成摘要
    const summary = this.generateSummary(
      typeErrors.length,
      enumErrors.length,
      unknownFields.length,
      missingRequiredFields.length
    );

    const result: AnalysisResult = {
      event: eventName,
      total_fields: totalFields,
      analyzed_fields: analyzedFields,
      type_errors: typeErrors,
      enum_errors: enumErrors,
      unknown_fields: unknownFields,
      coverage: `${coverage}%`,
      summary,
    };

    if (checkRequired) {
      result.missing_required_fields = missingRequiredFields;
    }

    return result;
  }

  /**
   * 比较两个事件的字段差异
   */
  compareEvents(fields1: FieldDefinitions, fields2: FieldDefinitions): ComparisonResult {
    const fields1Keys = new Set(Object.keys(fields1));
    const fields2Keys = new Set(Object.keys(fields2));

    const commonFields = [...fields1Keys].filter((key) => fields2Keys.has(key));
    const onlyInEvent1 = [...fields1Keys].filter((key) => !fields2Keys.has(key));
    const onlyInEvent2 = [...fields2Keys].filter((key) => !fields1Keys.has(key));

    // 检查类型差异
    const typeDifferences = commonFields
      .map((field) => {
        const type1 = fields1[field].type;
        const type2 = fields2[field].type;
        if (type1 !== type2) {
          return {
            field,
            event1_type: type1,
            event2_type: type2,
          };
        }
        return null;
      })
      .filter((item) => item !== null) as Array<{
      field: string;
      event1_type: string;
      event2_type: string;
    }>;

    return {
      event1: '',
      event2: '',
      common_fields: commonFields,
      only_in_event1: onlyInEvent1,
      only_in_event2: onlyInEvent2,
      type_differences: typeDifferences,
    };
  }

  /**
   * 映射 API 类型到 TypeName
   */
  private mapTypeToTypeName(apiType: string): TypeName {
    const typeMap: Record<string, TypeName> = {
      NUMBER: 'NUMBER',
      STRING: 'STRING',
      BOOL: 'BOOL',
      LIST: 'LIST',
      OBJECT: 'OBJECT',
      INT: 'NUMBER',
      FLOAT: 'NUMBER',
      BOOLEAN: 'BOOL',
      ARRAY: 'LIST',
      JSON: 'OBJECT',
    };

    const upperType = apiType.toUpperCase();
    return typeMap[upperType] || 'UNKNOWN';
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

  /**
   * 生成分析摘要
   */
  private generateSummary(
    typeErrorCount: number,
    enumErrorCount: number,
    unknownFieldCount: number,
    missingFieldCount: number
  ): string {
    const issues: string[] = [];

    if (typeErrorCount > 0) {
      issues.push(`${typeErrorCount} 个类型错误`);
    }
    if (enumErrorCount > 0) {
      issues.push(`${enumErrorCount} 个枚举值错误`);
    }
    if (unknownFieldCount > 0) {
      issues.push(`${unknownFieldCount} 个未知字段`);
    }
    if (missingFieldCount > 0) {
      issues.push(`${missingFieldCount} 个缺失必填字段`);
    }

    if (issues.length === 0) {
      return '✅ 数据完全符合规范';
    }

    return `⚠️ 发现问题：${issues.join('，')}`;
  }
}
